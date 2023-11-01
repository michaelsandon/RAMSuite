from app.examples import bp
from flask import render_template
import markdown
import app.static.helpers.global_formatting_functions as gff

@bp.route('/')
def index():
  return render_template('examples/index.html')

@bp.route('/survival/')
def survival():
  mkdwnex1 = gff.helper_read_and_format_markdown('app/examples/examples1.md')
  #mkdwn = markdown.markdownFromFile(input='app/examples/examples1.md')
  return render_template('examples/survival.html', mkdwnex1 = mkdwnex1)