# Scheduler
> Period send report data

## Install dependencies
```bash
# PhantomJS
# link: http://phantomjs.org/download.html

# install PhantomJS on macOS
brew install phantomjs

# install PhantomJS on centOS
wget --no-check-certificate https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
tar xvf phantomjs-2.1.1-linux-x86_64.tar.bz2
cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin

# install Chinese font(SimHei) for PhantomJS on centOS
mkdir /usr/share/fonts/
wget http://f.feei.cn/simhei.ttf
cp simhei.ttf /usr/share/fonts/
fc-cache -fv
```
## Configuration cron
```bash
# /etc/cron.weekly/cobra
0 0 * * 5 /usr/local/bin/phantomjs /you/path/cobra/cobra.py report -t=w > /dev/null
```