accountlist=['Contacts',['Name:',['Skype:','Gmail:','Mobile:','Home:']],
        ['CPH', ['apacph', 'apacph', '0910-335-513', '(07)722-3586']], 
        ['富涵',[ 'karina_chang24', 'karina5725', '0926-659-999', '(07)588-5725']],
        ['舜翔 (鳳眼)',[ 'agg2567', 'agg2567', '0933705207', '(037)673188']],
        ['琮貿 (港哥)',[ 'fcm021', 'kevin255466', '0930-809-805', '(07)806-6647']],
        ['新強', ['j86050123', 'j86050123456', '0939-866-546', '(03)932-1328']],
        ['品堯', ['liberte1124', 'wpinyao', '0975-221-172', '']],
        ['英凱', ['cs_sc_aoc', 'csscaoc', '0934-067539', '(04)22150398']],
        ['新捷', ['stevenolando', 'stevenolando', '0958-460-047', '(04)24262000']],
        ['逸民', ['future801113', 'future801113', '0953-340-305', '(02)22675029']],
        ['容宇', ['yujung0007', 'yujung0007', '0928-609-308', '(06)215-6479']],
        ['宜樺', ['ivoryfeather', 'acoldice', '0929-550-468', '(06)331-6798']],
        ['哲庸', ['pmcheng99', 'pmcheng99', '0939-826-043', '(02)2309-7134']],
        ['信宇', ['superjjj801', 'joshuahysu', '0922-388-872', '(03)5670386']],
        ['冠彰', ['m070888', 'm070888', '0922-200-238', '(02)2688-1347']],
        ['文成', ['sylvanasrin', 'iriairis5', '0933-758-332', '(02)2204-4312']]]
def print_lol(acc,indent=False,level=0):
	count=0
	while count < len(acc):
		if isinstance(acc[count],list):
			print_lol(acc[count],indent,level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t",end='')
			print(acc[count])
		count =count+1
print_lol(accountlist,True,0)
