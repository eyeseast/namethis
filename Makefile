

data/names.zip:
	mkdir -p $(dir $@)
	wget -O $@ http://www.ssa.gov/oact/babynames/names.zip

data/names/yob2013.txt: data/names.zip
	mkdir -p $(dir $@)
	unzip -d $(dir $@) -n data/names.zip

db: data/names/yob2013.txt
	if [ !$(DATABASE_URL) ]; then export DATABASE_URL=sqlite:///names.db; fi
	python bin/ingest.py $(DATABASE_URL)

redis: db
	if [ !$(REDIS_URL) ]; then export REDIS_URL="redis://localhost:6379/1"; fi
	python bin/load_redis.py $(DATABASE_URL) $(REDIS_URL)

clean:
	if [ -d data ]; then rm -rf data; fi