#!/usr/bin/env ruby
#

require "net/https"
require 'rubygems'
require 'json'

unless ARGV[2] && ARGV[3]
  puts 'You need to supply TOKEN (api-key) as third argument and user key as fourth argument'
  exit
end

TOKEN = ARGV[2]
USER  = ARGV[3]
MAX_URL = 512
MAX_URL_TITLE = 100
MAX_TITLE = 250
MAX_BODY = 1024

def truncate s, length = MAX_URL_TITLE, ellipsis = '…'
  if s.length > length
    s.to_s[0..length-ellipsis.bytesize].gsub(/[^\w]\w+\s*$/, ellipsis)
  else
    s
  end
end

def parse_issue(payload)
  issue = payload['issue']
  title = "#{issue['user']['login']} #{payload['action']} issue '#{issue['title']}'"
  labels = " (#{issue['labels'].join ', '})" if issue['labels'].any?
  message = "#{payload['repository']['full_name']} issue ##{issue['number']}#{labels}:\n#{issue['body']}"
  url = issue['html_url']
  url_title = 'View issue on GitHub'
  {url: url, title: title, message: message, url_title: url_title}
end

def parse_push(p)
  commit_count = p['commits'].size
  commit_str = "#{commit_count} commits " if commit_count > 1
  title = "#{p['pusher']['name']} pushed #{commit_str}to #{p['repository']['full_name']}"
  first_commit = p['commits'].first
  message = "#{"Latest (" + first_commit['id'][0..7] + "):\n" if commit_count > 1}#{first_commit['message']}"

  url = p['compare']
  url_title = "Compare on GitHub"
  {url: url, title: title, message: message, url_title: url_title}
end

unless ARGV[0]
  puts 'No GitHub-json supplied as first argument'
  exit
end
unless ARGV[1]
  puts 'No type supplied'
  exit
end


payload = JSON.parse(ARGV[0])
type = ARGV[1]

data = send "parse_#{type}", payload
if data[:url].size > MAX_URL
  puts "URL too long. Maximum 512 chars. Size: #{url.size}"
  exit
end

push_url = URI.parse("https://api.pushover.net/1/messages.json")
req = Net::HTTP::Post.new(push_url.path)
req.set_form_data({
   :token => TOKEN,
   :user => USER,
   :title => (truncate data[:title], MAX_TITLE),
   :message => (truncate data[:message], MAX_BODY),
   :url => data[:url],
   :url_title => (truncate data[:url_title], MAX_URL_TITLE)
})

res = Net::HTTP.new(push_url.host, push_url.port)
res.use_ssl = true
res.verify_mode = OpenSSL::SSL::VERIFY_PEER
res.start {|http| http.request(req) }

puts data[:title]
puts data[:message]
puts data[:url_title]
puts data[:url]
