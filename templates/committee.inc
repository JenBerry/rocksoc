{% if error %}
	No committee information: {{error}}
{% endif %}
{% if committee_members %}
	<div class="committee">
		<table>
			{% for Committee in committee_members %}
				<tr class="committee_info" id="committee-member-{{ Committee.name|slugify }}">
					<td class="committee_image"
						{% if Committee.description %}
							rowspan="2"
						{% endif %}
					>
						{% if Committee.image %}
							<img src="{{Committee.image}}" width="100" alt="({{Committee.name}} picture)" />
						{% endif %}
					</td>
					<td class="position"> {{Committee.position}}:</td>
					<td>{{Committee.name}}</td>
				</tr>
				{% if Committee.description %}
					<tr class="committee_desc">
						<td colspan="2">{{Committee.description}}</td>
					</tr>
				{% endif %}
			{% endfor %}
		</table>
	</div>
{% endif %}
