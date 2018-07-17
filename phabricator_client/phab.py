import calendar
import time

from phabricator import Phabricator
phab = Phabricator()  # This will use your ~/.arcrc file
# r = phab.user.find(aliases=["dzomer"])

DAY = 60*60*24

def get_name_from_phid(phid):
	r = phab.phid.query(phids=[phid])
	if phid in r:
		return r[phid]["name"]
	return "INVALID"

def list_names(names):
	names = list(names)
	if len(names) == 0:
		return ""
	if len(names) == 1:
		return names[0]
	ret = names[0]
	for name in names[1:-1]:
		ret += ", " + name 
	ret += " and " + names[-1]
	return ret

def get_work(name="dzomer", days=7):
	print "{} work state for the last {} days:".format(name, days)
	print "========================================================"
	state = ["Currently"]
	def is_relevant(task):
		if d["fields"]["status"]["value"] == "open":
			return True
		closed = d["fields"]["dateClosed"]
		curr_time = calendar.timegm(time.gmtime())
		if closed and curr_time - closed < days * DAY:
			state[0] = "Finished"
			return True
		return False
	constraints = dict(assigned=[name])
	res =  phab.maniphest.search(constraints=constraints)
	for d in res.data:
		if is_relevant(d):
			title = d["fields"]["name"].rstrip()
			title = title.lower()
			print "{} working on {} - T{}".format(state[0], title, d["id"])
			state = ["Currently"]
			priority = d["fields"]["priority"]["name"]
			added_comments = False
			#print phab.maniphest.info(task_id=d["id"]).keys()
			if state[0] != "Finished":
				transactions = phab.maniphest.gettasktransactions(ids=[d["id"]])[str(d["id"])]
				commenters = set()
				for t in transactions:
					if t["comments"]:
						commenter = get_name_from_phid(t["authorPHID"])
						if name in t["comments"].lower():
							commenters.add(commenter)
						if name == commenter:
							added_comments = True
						#print "{}: {}".format(get_name_from_phid(t["authorPHID"]), t["comments"])
					#print t.keys()
				if added_comments:
					print "Added comments"
				if len(commenters) > 0:
					print "Working on comments from {}".format(list_names(commenters))
			print "*"
			#print transactions
get_work(name="maor")
"""
res.data
r = res.data[0]
r["fields"]
"""