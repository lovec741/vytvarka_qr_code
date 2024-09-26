from app import create_app, db
import logging

app = create_app()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully.")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")

    try:
        app.run("0.0.0.0", debug=True, use_reloader=False)
    except Exception as e:
        app.logger.error(f"Error running the app: {str(e)}")