from app.resources import bp
from flask import render_template, jsonify
import markdown
import app.static.helpers.global_formatting_functions as gff
from app.resources.static.resourceindex import resources
from linkpreview import link_preview

resources = resources()
resources["img_src"] = "data:,"
for r in resources.itertuples():
  if r.url is not None:
    meta = link_preview(r.url)
    resources.loc[r.Index,"img_src"] = meta.absolute_image
    resources.loc[r.Index,"desc"] = meta.description
    

@bp.route('/standards_and_journals/')
def standards_and_journals():
  tiles = {"Standards":None,
          "Journals":None,
          "Blogs":resources.loc[resources.type=="blog"]}
  return render_template('resources/base.html', tiles = tiles, title = "Standards, Journals and Blogs")


@bp.route('/data/')
def data():
  tiles = {"Data":resources.loc[resources.type=="data"],
          "Templates":None}
  return render_template('resources/base.html', tiles = tiles, title = "Data and Templates")


@bp.route('/software/')
def software():
  tiles = {"Licensed Applications":resources.loc[resources.type=="software"],
           "Open Source Packages":None}
  return render_template('resources/base.html', tiles = tiles, title = "Software")