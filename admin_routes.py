"""
Admin routes — dashboard, component management.
Protected by login_required + admin_required decorators.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from functools import wraps
from database.db import db
from models.component import Component
from models.link      import Link
from models.user      import User
from models.build     import Build

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id") or not session.get("is_admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "components": Component.query.count(),
        "users":      User.query.count(),
        "builds":     Build.query.count(),
        "links":      Link.query.count(),
    }
    recent_builds = Build.query.order_by(Build.created_at.desc()).limit(10).all()
    recent_users  = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats,
                           recent_builds=recent_builds, recent_users=recent_users)


@admin_bp.route("/components")
@admin_required
def manage_components():
    category = request.args.get("category", "")
    search   = request.args.get("search", "")
    q = Component.query
    if category:
        q = q.filter_by(category=category)
    if search:
        q = q.filter(Component.name.ilike(f"%{search}%"))
    components = q.order_by(Component.category, Component.name).all()
    categories = db.session.query(Component.category).distinct().all()
    return render_template("admin/manage_components.html",
                           components=components,
                           categories=[c[0] for c in categories],
                           search=search, active_category=category)


@admin_bp.route("/components/add", methods=["POST"])
@admin_required
def add_component():
    c = Component(
        name=request.form["name"], brand=request.form["brand"],
        category=request.form["category"], price=int(request.form["price"]),
        specs=request.form.get("specs", ""),
    )
    db.session.add(c)
    db.session.commit()
    flash(f"Component '{c.name}' added.", "success")
    return redirect(url_for("admin.manage_components"))


@admin_bp.route("/components/edit/<int:cid>", methods=["POST"])
@admin_required
def edit_component(cid):
    c = Component.query.get_or_404(cid)
    c.name     = request.form["name"]
    c.brand    = request.form["brand"]
    c.category = request.form["category"]
    c.price    = int(request.form["price"])
    c.specs    = request.form.get("specs", "")
    db.session.commit()
    flash(f"Component '{c.name}' updated.", "success")
    return redirect(url_for("admin.manage_components"))


@admin_bp.route("/components/delete/<int:cid>", methods=["POST"])
@admin_required
def delete_component(cid):
    c = Component.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash(f"Deleted '{c.name}'.", "warning")
    return redirect(url_for("admin.manage_components"))
