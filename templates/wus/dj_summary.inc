{% load rocksoc_html %}
{# Summary for each DJ #}
{% if not dj_on_own_page %}
<h2><a href="/wus/dj/{{ dj.userid }}">{{ dj.name }}</a></h2>
{% endif %}
{% if dj.plays %}<p class="strong">{{ dj.plays }}</p>{% endif %}
<p class="heading">Sets ({{ dj.sets|length }} in total):</p>
{% if dj.sets %}
<ul class="dj-sets">
	{% for set in dj.sets reversed %}
	<li>
		<a href="{% if not dj_on_own_page %}/wus/dj/{{ dj.userid }}/{% endif %}#wus-set-{{ set.event.edatetime|date:"Ymd" }}-{{ set.start|time:"Hi" }}">{{ set.event.edatetime|date:"jS N Y" }} {{ set.start|time:"H:i" }}&ndash;{{ set.end|time:"H:i" }}</a> &mdash; {{ set.playing }}
		{% ifnotequal dj.userid set.dj.userid %}
		(with
			{% for other in set.dj.represents_djs.all|listexclude:dj %}
			<a href="/wus/dj/{{ other.userid }}/">{{ other.name }}</a>
			{% if not forloop.last %}, {% endif %}
			{% endfor %}
		)
		{% endifnotequal %}
	</li>
	{% endfor %}
</ul>
{% endif %}
