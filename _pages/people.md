---
layout: page
title: People
permalink: /people/
description: Group members
nav: true
nav_order: 2
---

{% assign sections = "pi,phd,ms,visiting,alumni" | split: "," %}

{% for sec in sections %}
  {% assign members = site.people | where: "role", sec | sort: "order" %}
  {% if members.size > 0 %}

  {% case sec %}
    {% when "pi" %} <h2>Principal Investigator</h2>
    {% when "phd" %} <h2>PhD Students</h2>
    {% when "ms" %} <h2>MS Students</h2>
    {% when "visiting" %} <h2>Visiting Students</h2>
    {% when "alumni" %} <h2>Alumni</h2>
  {% endcase %}

  <div class="row">
    {% for p in members %}
      <div class="col-12 col-sm-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm">
          {% if p.photo %}
            <img class="card-img-top" src="{{ '/assets/img/' | append: p.photo | relative_url }}" alt="{{ p.name }}">
          {% endif %}
          <div class="card-body">
            <h5 class="card-title mb-1">
              <a href="{{ p.url | relative_url }}">{{ p.name }}</a>
            </h5>
            <div class="text-muted mb-2">
              {% if p.title %}{{ p.title }}{% endif %}
              {% if p.affiliation %}{% if p.title %}, {% endif %}{{ p.affiliation }}{% endif %}
            </div>

            <div class="small">
              {% if p.email %}<div><a href="mailto:{{ p.email }}">{{ p.email }}</a></div>{% endif %}
              {% if p.website %}<div><a href="{{ p.website }}">Website</a></div>{% endif %}
              {% if p.scholar %}<div><a href="{{ p.scholar }}">Google Scholar</a></div>{% endif %}
              {% if p.github %}<div><a href="{{ p.github }}">GitHub</a></div>{% endif %}
            </div>

            {% if sec == "alumni" %}
              <hr class="my-2">
              <div class="small">
                {% if p.alumni_year %}<div><b>Alumni:</b> {{ p.alumni_year }}</div>{% endif %}
                {% if p.next_position %}<div><b>Next:</b> {{ p.next_position }}</div>{% endif %}
              </div>
            {% endif %}
          </div>
        </div>
      </div>
    {% endfor %}
  </div>

  {% endif %}
{% endfor %}