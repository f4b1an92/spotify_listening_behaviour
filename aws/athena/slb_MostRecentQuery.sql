SELECT *
FROM spotifylisteningbehaviour.rawdata
WHERE id != 'id' -- avoids having column header of each csv-file being part of the the results
	- -
	AND played_at >= '2025-09-01';