FROM jekyll/jekyll:4
MAINTAINER Tim Byrne <sultan@locehilios.com>

# Convenience settings for the testbed's root account
RUN echo 'set -o vi' >> /root/.bashrc

# Create a flag to identify when running inside the yadm/jekyll image
RUN touch /.yadmjekyll

# Extra dependencies for testing
# RUN gem install zeitwerk -v 2.6.18
# RUN gem install nokogiri -v 1.15.6
# RUN gem install webrick
RUN gem uninstall html-proofer
RUN gem install html-proofer -v '~> 3'
RUN apk add --update py-pip
RUN pip install yamllint==1.15.0
