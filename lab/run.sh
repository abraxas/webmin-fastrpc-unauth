#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-webminh02}"
export PYTHONUNBUFFERED=1

LABEL="WEBMIN-H02-FASTRPC"
WITNESS="WEBMIN-H02-FASTRPC"
IMAGE="webmin-lab:2.670"
LOCK="/tmp/webmin-lab-image.lock"
BASE="http://127.0.0.1:18480"
PIN_TAG="2.670"
PIN_SHA="3a2b2b8671c0669c129f5275b3dd1853106ae02b"
REPO_URL="${WEBMIN_SRC_URL:-https://github.com/webmin/webmin.git}"
SRC_DIR="$(pwd)/src"
DOCKERFILE="$(pwd)/Dockerfile"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  echo "FAIL ${LABEL} $* ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  exit 1
}

clone_pin() {
  if [[ -d "${SRC_DIR}/.git" ]]; then
    local got
    got="$(git -C "${SRC_DIR}" rev-parse HEAD)"
    if [[ "${got}" == "${PIN_SHA}" ]]; then
      echo "IOC checkout-ok tag=${PIN_TAG} sha=${got} source=existing-clone"
      return 0
    fi
    echo "IOC reclone tag=${PIN_TAG} got=${got} expect=${PIN_SHA}"
    rm -rf "${SRC_DIR}"
  elif [[ -e "${SRC_DIR}" ]]; then
    echo "IOC reclone tag=${PIN_TAG} source=non-git-src"
    rm -rf "${SRC_DIR}"
  fi
  echo "== git clone --depth 1 --branch ${PIN_TAG} =="
  GIT_TERMINAL_PROMPT=0 git clone --depth 1 --branch "${PIN_TAG}" \
    "${REPO_URL}" "${SRC_DIR}" || fail_setup "clone-failed"
  local got
  got="$(git -C "${SRC_DIR}" rev-parse HEAD)"
  if [[ "${got}" != "${PIN_SHA}" ]]; then
    GIT_TERMINAL_PROMPT=0 git -C "${SRC_DIR}" fetch --depth 1 origin "${PIN_SHA}" \
      || fail_setup "fetch-failed"
    git -C "${SRC_DIR}" checkout -f "${PIN_SHA}" || fail_setup "checkout-failed"
    got="$(git -C "${SRC_DIR}" rev-parse HEAD)"
  fi
  if [[ "${got}" != "${PIN_SHA}" ]]; then
    fail_setup "pin-mismatch got=${got} expect=${PIN_SHA}"
  fi
  if [[ ! -f "${SRC_DIR}/setup.sh" || ! -f "${SRC_DIR}/fastrpc.cgi" ]]; then
    fail_setup "missing-fastrpc-tree"
  fi
  echo "IOC checkout-ok tag=${PIN_TAG} sha=${got} source=git-clone"
}

ensure_image() {
  python3 - "${LOCK}" "${IMAGE}" "${DOCKERFILE}" "${SRC_DIR}" <<'PY'
import fcntl
import os
import subprocess
import sys

lock_path, image, dockerfile, src = sys.argv[1:5]
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o666)
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        check=False,
    )
    if inspect.returncode == 0:
        print(f"IOC reuse-image {image}", flush=True)
        raise SystemExit(0)
    print(f"IOC build-image {image}", flush=True)
    raise SystemExit(
        subprocess.call(["docker", "build", "-t", image, "-f", dockerfile, src])
    )
finally:
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
PY
}

trap down EXIT

echo "== py_compile poc.py =="
python3 -m py_compile poc.py

echo "== docker compose down (clean) =="
down
docker network prune -f >/dev/null 2>&1 || true

echo "== pin ${PIN_TAG} ${PIN_SHA} =="
clone_pin

echo "== ensure ${IMAGE} =="
ensure_image || fail_setup "image-build-failed"

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 12); do
  docker network prune -f >/dev/null 2>&1 || true
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=${attempt}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait ${BASE}/session_login.cgi =="
ready=0
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/webmin-h02-ready.html -w '%{http_code}' --max-time 8 \
    "${BASE}/session_login.cgi" || true)"
  if [[ "${code}" == "200" || "${code}" == "401" ]]; then
    ready=1
    echo "IOC login-ready attempt=${i} http=${code}"
    break
  fi
  echo "IOC login-wait attempt=${i} http=${code}"
  sleep 2
done
if [[ "${ready}" != 1 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  fail_setup "login-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e

if ! tail -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit=${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

if [[ "${rc}" != 0 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
fi

exit "${rc}"
