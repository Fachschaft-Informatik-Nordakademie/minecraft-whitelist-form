import mc_whitelist_form

if __name__ == '__main__':
    app = mc_whitelist_form.create_app()
    app.run(debug=True, port=4200)
