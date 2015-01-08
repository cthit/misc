#!/usr/bin/env ruby
# encoding: utf-8
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
ELLIPSIS = '…'

def allowed_type?(type)
  # TODO: issue_comment, member, pull_request, repository and team_add
  valid_types = ['push', 'issues'].freeze
  unless valid_types.include? type
    puts type + ' is not a supported type. Supports ' + valid_types.to_s
    exit
  end
end

def truncate s, length = MAX_URL_TITLE, ellipsis = ELLIPSIS
  if s.length > length
    s.to_s[0..length-ellipsis.bytesize].gsub(/[^\w]\w+\s*$/, ellipsis)
  else
    s
  end
end


def parse_issues(payload)
  issue = payload['issue']
  action = payload['action']
  ignore = ['unassigned', 'labeled', 'unlabeled']
  if ignore.include? action
    puts "Issue parsing: ignoring action '#{action}'"
    exit
  end

  repo = payload['repository']['full_name']
  issue_num = issue['number']
  issuee = issue['user']['login']
  issue_title = issue['title']

  case action
  when "assigned"
    assignee = payload['assignee']['login']
    message = "#{assignee} were assigned to '#{issue_title}'"
  else
    message = issue_title
  end

  title = "#{issuee} #{action} issue #{repo}##{issue_num}"
  url = issue['html_url']
  url_title = 'View issue on GitHub'
  {url: url, title: title, message: message, url_title: url_title}
end

def parse_push(p)
  pushee = p['pusher']['name']
  branch = p['ref'].split('/').last
  repo = p['repository']['full_name']

  message = p['commits'].map do |c|
    parts = c['message'].partition "\n\n"
    msg = parts.first
    msg += " #{ELLIPSIS}" unless parts.last.empty?

    "#{c['id'][0..6]} #{msg}"
  end

  url = p['compare']
  url_title = "Compare on GitHub"
  title = "#{pushee} pushed to #{branch} at #{repo}"
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
allowed_type? type

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
