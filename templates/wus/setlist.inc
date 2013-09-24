{% load rocksoc_html %}
{# Markup for individual sets, list of tracks #}
{# Header #}
<p class="strong no-link">
	{# DJ #}
	{% if not dj_on_own_page %}
	<a href="/wus/dj/{{ set.dj.userid }}/">{{ set.dj.name }}</a>
	{% else %}
	{% ifnotequal dj.userid set.dj.userid %}
		with
			{% for other in set.dj.represents_djs.all|listexclude:dj %}
			<a href="/wus/dj/{{ other.userid }}/">{{ other.name }}</a>
			{% if not forloop.last %}, {% endif %}
			{% endfor %}
	{% endifnotequal %}
	{% endif %}
	{# Puts date and time in header, and links to the page for that WUS #}
	<a href="/wus/date/{{ set.event.edatetime|date:"Y-m-d" }}/" name="wus-set-{{ set.event.edatetime|date:"Ymd" }}-{{ set.start|time:"Hi" }}" id="wus-set-{{ set.event.edatetime|date:"Ymd" }}-{{ set.start|time:"Hi" }}">{{ set.event.edatetime|date:"jS N Y" }}</a>
	{{ set.start|time:"H:i" }}&ndash;{{ set.end|time:"H:i" }}
	{# Description of set #}
	{% if set.playing %} &mdash; {{ set.playing }}{% endif %}
</p>
<div class="track-list">
{# List of sets #}
	{% if set.setlist %}
	<table>
		{% for setlist_item in set.setlist %}
		<tr>{% include "wus/setlist_item.inc" %}</tr>
		{% endfor %}
	</table>
	{% else %}
	<p>No set list information available for this set.</p>
	{% endif %}
</div>
