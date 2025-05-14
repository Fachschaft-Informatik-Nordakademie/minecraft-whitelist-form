FROM arm64v8/python:3.13-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install waitress
COPY mc_whitelist_form mc_whitelist_form
EXPOSE 80
CMD ["/bin/bash", "-c", "flask --app mc_whitelist_form init-db --no-force && waitress-serve --port=80 --call mc_whitelist_form:create_app"]
