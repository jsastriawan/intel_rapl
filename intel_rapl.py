#
# Intel RAPL energy counter agent
#
import os
import collectd

rapl_basepath = "/sys/devices/virtual/powercap/intel-rapl"
rapl_domain = {}

PLUGIN_NAME = 'intel-rapl'

def detect_rapl_domain(bpath):
	for fname in os.listdir(bpath):
		if fname.startswith('intel-rapl'):
			fldr = os.path.join(bpath,fname)
			nm = os.path.join(fldr,'name')
			if os.path.isfile(nm):
				with open(nm,'r') as fnm:
					nmstr = fnm.read().rstrip('\n')
					fnm.close()
					rapl_domain[nmstr]=fldr
			detect_rapl_domain(fldr)

def read_energy_uj(domain):
	ret = 0
	if domain is not None and domain in rapl_domain:
		fpath = os.path.join(rapl_domain[domain],'energy_uj')
		if os.path.isfile(fpath):
			with open(fpath,'r') as f:
				ret = f.read().rstrip('\n')
				f.close()
	return int(ret)

def rapl_init():
	detect_rapl_domain(rapl_basepath)
	collectd.info("%s: %s" % (PLUGIN_NAME,"Initialized"))

def rapl_read():
	val = {}
	# read all
	for d in rapl_domain:
		val[d] = read_energy_uj(d)
	# dispatch
	for dm in val:
		collectd.Values(plugin=PLUGIN_NAME, 
			type_instance=dm, 
			type='counter', 
			values=[val[dm]]).dispatch()

def rapl_config(conf):
	collectd.info("%s: %s" % (PLUGIN_NAME,"Configured"))

if __name__!="__main__":
	collectd.register_config(rapl_config)
	collectd.register_read(rapl_read)
	collectd.register_init(rapl_init)

