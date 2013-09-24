{% load rocksoc_html %}
{# An instance of a track in a WUS set #}
<td>{{ setlist_item.num|add:"1" }}.</td>
<td>
	{% if not track_on_own_page %}
	<a href="/wus/track/{{ setlist_item.track.id|urlencode|escape }}/">
	{% endif %}
	{{ setlist_item.track.name }}
	{% if not track_on_own_page %}
	</a>
	{% endif %}
</td>
<td>
	{% if not artist_on_own_page %}
	<a href="/wus/artist/{{ setlist_item.artist.id|urlencode|escape }}/">
	{% endif %}
	{{ setlist_item.artist.name }}
	{% if not artist_on_own_page %}
	</a>
	{% endif %}
</td>
<td>
	{% if setlist_item.request %}
	<span class="request">(R)</span>
	{% endif %}
	{% if setlist_item.lp %}
	[{% if setlist_item.track_on_lp %}track {{ setlist_item.track_on_lp }}, {% endif %}<em class="albumname">{{ setlist_item.lp }}</em>{% if setlist_item.year %}, {{ setlist_item.year }}{% endif %}]
	{% endif %}
</td>
