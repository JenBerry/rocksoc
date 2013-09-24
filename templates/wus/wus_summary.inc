{% load rocksoc_html %}
<div class="no-link wus-box">
	<div class="wus-heading">
		<p class="strong"><a href="/wus/date/{{ wus.edatetime|date:"Y-m-d" }}/">{{ wus.edatetime|date:"jS N Y" }}</a>: {{ wus.edatetime|time:"H:i" }}&ndash;{{ wus.finish_time|time:"H:i" }} &mdash;
		{% if wus.venue.use_our_page %}
			<a href="/venues/{{ wus.venue.id|escape }}/">
		{% else %}
		{% if wus.venue.website %}
			<a href="{{ wus.venue.website|escape }}">
		{% endif %}
		{% endif %}
		{{ wus.venue.name }}
		{% if wus.venue.use_our_page or wus.venue.website %}
			</a>
		{% endif %}</p>
	</div>
	<table class="wus-info">
		<tr>
			<th class="wus-slot">Slot</th>
			<th>DJ</th>
			<th>Info</th>
		</tr>
		{% for set in wus.wus_sets.all %}
		<tr>
			<td>{{ set.start|time:"H:i" }}&ndash;{{ set.end|time:"H:i" }}</td> 
			<td><a href="/wus/dj/{{ set.dj.userid }}/">{{ set.dj.name }}</a></td>
			<td>{{ set.playing }}</td>
		</tr>
		{% endfor %}
	</table>
</div>
