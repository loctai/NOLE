celery -A app.tasks.tasks worker -l info -P eventlet


pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d app/translations

pybabel compile -d app/translations
# NOLE Crontab
0/30 * * * * curl http://localhost:5889/jobs/auto-tickers
0 21 * * * curl http://localhost:5889/jobs/jobs-reset-maxout-profitday
5 21 * * *  curl http://localhost:5889/jobs/jobs-profit-daily
30 21 * * * curl http://localhost:5889/jobs/jobs-binary-bonus
0 22 * * * curl http://localhost:5889/jobs/jobs-auto-withdraw-profit


[SSL: CERTIFICATE_VERIFY_FAILED]
 sudo update-ca-certificates --fresh
$ export SSL_CERT_DIR=/etc/ssl/certs