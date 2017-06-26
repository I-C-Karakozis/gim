from flask import render_template
from itsdangerous import URLSafeTimedSerializer

from app import app, db
from app.mod_api import models

@app.route('/Confirm/<token>')
def confirm_email(token):
	ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		email = ts.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=86400)
	except:
		abort(404)

	user = models.User.query.filter_by(email=email).first_or_404()

	user.confirmed = True

	db.session.add(user)
	db.session.commit()

	return render_template('activated.html')