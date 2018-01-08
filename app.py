from flask import Flask, flash, redirect, render_template, request, session, abort
from backend import Quiz
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'buzzfeed-sucks'



class LoginForm(FlaskForm):
    siteurl = StringField('Quiz URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/", methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        url=form.siteurl.data
        shortened=url[url.index('.com')+4:]
        return redirect(shortened)
    return render_template('index.html', title='Sign In', form=form)

@app.route("/<string:first>/<string:rest>/")
def solver(first,rest):
    solutions=Quiz.url_to_quiz("https://www.buzzfeed.com/"+first+"/"+rest)
    title=solutions.get_title()
    top_row=solutions.get_top_row()
    users=solutions.get_results()
    questions=solutions.get_questions()

    #questions=[(option['header'],option['description'],option['image'],[(a['personality_index'], a['header'])for a in option['answers']].sort(key=lambda x:x[0])) for option in questions_data]
    #questions=[(option['header'],option['description'],option['image'],sorted([(a['personality_index'], a['header'],a)for a in option['answers']],key=lambda x:x[0])) for option in questions_data]

    return render_template('solution.html',**locals())


if __name__ == "__main__":
    app.run()
