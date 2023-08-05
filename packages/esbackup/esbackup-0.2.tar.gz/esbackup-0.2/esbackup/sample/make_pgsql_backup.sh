#!/bin/sh
#

err() {
	echo "Error: $2" >&2
	exit $1
}
log() {
	echo "Log:   $1" >&2
}

HOST="$1"
PGSQL_USER="$2"
DATABASE="$3"
DUMPFILE="$4"
PORT="5432"

[ -z "${HOST}" ] && err 1 "Host not specified"
[ -z "${PGSQL_USER}" ] && err 1 "User not specified"
[ -z "${DATABASE}" ] && err 1 "Database not specified"
[ -z "${DUMPFILE}" ] && err 1 "Dump file prefix not specified"

pg_dump="pg_dump"

rm -f "${DUMPFILE}.schema.dump"
rm -f "${DUMPFILE}.data.dump"
${pg_dump} -U "${PGSQL_USER}" -w -h "${HOST}" -p "${PORT}" --format=c -s "${DATABASE}" --file="${DUMPFILE}.schema.dump" 2>&1 < /dev/null
${pg_dump} -U "${PGSQL_USER}" -w -h "${HOST}" -p "${PORT}" --format=c -a "${DATABASE}" --file="${DUMPFILE}.data.dump"   2>&1 < /dev/null

