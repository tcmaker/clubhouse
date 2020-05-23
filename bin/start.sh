if [ "$ENVIRONMENT" -eq "development" ]; then
  exec pipenv ./manage.py runsslserver
else
  exec gunicorn clubhouse.wsgi
fi
