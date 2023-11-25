from app.resources import bp
from flask import render_template, jsonify
import markdown
import app.static.helpers.global_formatting_functions as gff
from app.resources.static.resourceindex import resources
from linkpreview import link_preview

resources = resources()    

@bp.route('/standards_and_journals/')
def standards_and_journals():
  r_sub = resources.loc[resources.type=="blog"]
  tiles = {"Standards":None,
          "Journals":None,
          "Blogs":get_linkpreviews(r_sub)}
  return render_template('resources/base.html', tiles = tiles, title = "Standards, Journals and Blogs")


@bp.route('/data/')
def data():
  r_sub = resources.loc[resources.type=="data"]
  tiles = {"Data":get_linkpreviews(r_sub),
          "Templates":None}
  return render_template('resources/base.html', tiles = tiles, title = "Data and Templates")


@bp.route('/software/')
def software():
  r_sub = resources.loc[resources.type=="software"]
  tiles = {"Licensed Applications":get_linkpreviews(r_sub),
           "Open Source Packages":None}
  return render_template('resources/base.html', tiles = tiles, title = "Software")

def get_linkpreviews(resource_subset):
  resource_subset["img_src"] = "data:,"
  for r in resource_subset.itertuples():
    if r.url is not None:
      meta = link_preview(r.url)
      resource_subset.loc[r.Index,"img_src"] = meta.absolute_image
      resource_subset.loc[r.Index,"desc"] = meta.description
  return resource_subset