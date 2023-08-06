<%def name="get_label_perf(avg_time)">
	% if avg_time > 1 :
		<span class="bad_perf">BAD</span>
	% elif avg_time > 0.6 :
		<span class="poor_perf">POOR</span>
	% elif avg_time > 0.3 :
		<span class="small_perf">SMALL</span>
	% else :
		<span class="good_perf">GOOD</span>
	% endif
</%def>

<%def name="get_color_perf(avg_time)">
	% if avg_time > 1 :
		<span class="bad_perf">${"%d"%(int(avg_time*1000.0))}</span>
	% elif avg_time > 0.6 :
		<span class="poor_perf">${"%d"%(int(avg_time*1000.0))}</span>
	% elif avg_time > 0.3 :
		<span class="small_perf">${"%d"%(int(avg_time*1000.0))}</span>
	% else :
		<span class="good_perf">${"%d"%(int(avg_time*1000.0))}</span>
	% endif
</%def>

<%def name="publish_url_row(id, request_avg_time, sql_avg_time, sql_nb_queries, url)">
	<tr>
		<td>${id}</td>
		<td>${get_color_perf(request_avg_time)}</td>
		<td>${get_label_perf(request_avg_time)}</td>
            % if sql_avg_time is not None and sql_avg_time >= 0 :
		<td>${get_color_perf(sql_avg_time)}</td>
            % else :
		<td>-</td>
            % endif
        <td>${sql_nb_queries}</td>
		<td>${url}</td>
	</tr>
</%def>

<%def name="publish_agg_routes_row(id, id_view, request_avg_time, sql_avg_time, sql_nb_queries, route_name, view_name, cpt)">
	<tr>
		<td>${id}</td>
		<td>${get_color_perf(request_avg_time)}</td>
		<td>${get_label_perf(request_avg_time)}</td>
            % if sql_avg_time is not None and sql_avg_time > 0 :
		<td>${get_color_perf(sql_avg_time)}</td>
            % else :
		<td>-</td>
            % endif
        <td>${sql_nb_queries}</td>
		<td>
				  <a href="${request.route_url("pyramid_perfstat.reporting.url_detail", id_session=id_session, id_view=id_view, id_route=id)}">${route_name}</a>
				</td>
		<td>${view_name}</td>
		<td>${cpt}</td>
	</tr>
</%def>

<%def name="publish_agg_view_row(id, request_avg_time, sql_avg_time, sql_nb_queries, view_name, cpt)">
	<tr>
		<td>${id}</td>
		<td>${get_color_perf(request_avg_time)}</td>
		<td>${get_label_perf(request_avg_time)}</td>
            % if sql_avg_time is not None and sql_avg_time > 0 :
		<td>${get_color_perf(sql_avg_time)}</td>
            % else :
		<td>-</td>
            % endif
        <td>${sql_nb_queries}</td>
		<td><a href="${request.route_url("pyramid_perfstat.reporting.view_detail",id_session=id_session, id_view=id)}">${view_name}</a></td>
		<td>${cpt}</td>
	</tr>
</%def>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">

<html>
	<head>
		<title>Perf manager</title>
		
		<style type="text/css">
<!--
.bad_perf {
	color:#A42020;
	font-weight: bold;
}
.poor_perf {
	color:#D78244;
	font-weight: bold;
}
.small_perf {
	color:#C4C200;
	font-weight: bold;
}
.good_perf {
	color:#4B855A;
	font-weight: bold;
}

/* tables */
table.tablesorter {
	font-family:arial;
	background-color: #CDCDCD;
	margin:10px 0pt 15px;
	font-size: 8pt;
	width: 100%;
	text-align: left;
}
table.tablesorter thead tr th, table.tablesorter tfoot tr th {
	background-color: #e6EEEE;
	border: 1px solid #FFF;
	font-size: 8pt;
	padding: 4px;
	padding-right: 20px;
}
table.tablesorter thead tr .header {
	background-image: url(${static_path}images/bg.gif);
	background-repeat: no-repeat;
	background-position: center right;
	cursor: pointer;
}
table.tablesorter tbody td {
	color: #3D3D3D;
	padding: 4px;
	background-color: #FFF;
	vertical-align: top;
}
table.tablesorter tbody tr.odd td {
	background-color:#F0F0F6;
}
table.tablesorter thead tr .headerSortUp {
	background-image: url(${static_path}images/asc.gif);
}
table.tablesorter thead tr .headerSortDown {
	background-image: url(${static_path}images/desc.gif);
}
table.tablesorter thead tr .headerSortDown, table.tablesorter thead tr .headerSortUp {
background-color: #8dbdd8;
}

#perf_views_reporting_table  tbody td:nth-child(1),
#perf_routes_reporting_table tbody td:nth-child(1),
#perf_urls_reporting_table   tbody td:nth-child(1) {
	width: 5%;
	min-width: 50px;
}

#perf_views_reporting_table  tbody td:nth-child(2),
#perf_routes_reporting_table tbody td:nth-child(2),
#perf_urls_reporting_table   tbody td:nth-child(2) {
	text-align: right;
	width: 5%;
	min-width: 50px;
}

#perf_views_reporting_table  tbody td:nth-child(3),
#perf_routes_reporting_table tbody td:nth-child(3),
#perf_urls_reporting_table   tbody td:nth-child(3) {
	width: 5%;
	min-width: 50px;
}

#perf_views_reporting_table  tbody td:nth-child(4),
#perf_routes_reporting_table tbody td:nth-child(4),
#perf_urls_reporting_table   tbody td:nth-child(4) {
	text-align: right;
	width: 5%;
	min-width: 30px;
}

#perf_views_reporting_table  tbody td:nth-child(5),
#perf_routes_reporting_table tbody td:nth-child(5),
#perf_urls_reporting_table   tbody td:nth-child(5) {
	text-align: right;
	width: 5%;
	min-width: 30px;
}

#perf_views_reporting_table  tbody td:nth-child(7),
#perf_routes_reporting_table tbody td:nth-child(8) {
	width: 5%;
	min-width: 50px;
}
-->
		</style>
		
	</head>
	<body>
		<select onchange="javascript:goTo('${request.route_url(route_name='pyramid_perfstat.reporting.session_detail',id_session='')}'+$(this).val());">
			% for id, dt_label, nb_rows in lst_ids_measures_date :
				<option value="${id}" ${"selected='selected'" if id==id_session else ''}>SESSION-${id}: ${dt_label} nb of records : ${nb_rows}</option>
			% endfor
		</select>
		
		<button onclick="goTo('${request.route_url(route_name='pyramid_perfstat.reset')}')">reset db</button>
		
		<br />
		<br />
		<table id="perf_views_reporting_table" class="tablesorter">
			<thead>
				<tr>
					<th>id</th>
					<th>avg&#160;time&#160;(ms)</th>
					<th>category</th>
					<th><b>sql avg</b><br/>&#160;time&#160;(ms)</th>
					<th>sql queries count</th>
					<th>matched view name</th>
					<th>view count</th>
				</tr>
			</thead>
			<tbody>
				% for (id, request_avg_time, sql_avg_time, sql_nb_queries, view_name, cpt) in lst_agg_views_measures :
					${publish_agg_view_row(id, request_avg_time, sql_avg_time, sql_nb_queries, view_name, cpt)}
				% endfor
			</tbody>
		</table>
		% if lst_agg_routes_measures is not None :
		<table id="perf_routes_reporting_table" class="tablesorter">
			<thead>
				<tr>
					<th>id</th>
					<th>avg&#160;time&#160;(ms)</th>
					<th>category</th>
					<th><b>sql avg</b><br/>&#160;time&#160;(ms)</th>
					<th>sql queries count</th>
					<th>matched route name</th>
					<th>matched view name</th>
					<th>url count</th>
				</tr>
			</thead>
			<tbody>
				% for (id, id_view, request_avg_time, sql_avg_time, sql_nb_queries, route_name, view_name, cpt) in lst_agg_routes_measures :
					${publish_agg_routes_row(id, id_view, request_avg_time, sql_avg_time, sql_nb_queries, route_name, view_name, cpt)}
				% endfor
			</tbody>
		</table>
		% endif
		% if lst_urls_measures is not None :
		<table id="perf_urls_reporting_table" class="tablesorter">
			<thead>
				<tr>
					<th>id</th>
					<th>avg&#160;time&#160;(ms)</th>
					<th>category</th>
					<th><b>sql avg</b><br/>&#160;time&#160;(ms)</th>
					<th>sql queries count</th>
					<th>requested url</th>
				</tr>
			</thead>
			<tbody>
				% for (id, request_avg_time, sql_avg_time, sql_nb_queries, url) in lst_urls_measures :
					${publish_url_row(id, request_avg_time, sql_avg_time, sql_nb_queries, url)}
				% endfor
			</tbody>
		</table>
		% endif
	</body>

	<script type="text/javascript" src="${static_path}js/jquery-1.6.4.min.js"></script>
	
	<script>
		function goTo(page)
		{
			window.location.assign(page);
		}

		$(document).ready(function() { 
			$("#perf_views_reporting_table").tablesorter({}); 
			
			$("#perf_routes_reporting_table").tablesorter({});
			
			% if lst_urls_measures is not None :
				$("#perf_urls_reporting_table").tablesorter({});
			% endif
		});
	</script>
</html>
