def get_total_cable_length( skeleton ):
	""" Return the sum of distances along edges of the
	skeleton graph. Requires labeling of skeleton edges
	with the distance property. """
	distance_sum = 0.0
	for u,v,d in skeleton.graph.edges_iter(data=True):
		distance_sum += d['distance']
	return distance_sum
