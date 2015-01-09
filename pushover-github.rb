#!/usr/bin/env ruby
# encoding: utf-8
#
require 'optparse'
require "net/https"
require 'rubygems'
require 'json'

MAX_URL = 512
MAX_URL_TITLE = 100
MAX_TITLE = 250
MAX_BODY = 1024
ELLIPSIS = '…'

options = {}
OptionParser.new do |opts|
  opts.banner = "usage: pushover-github.rb <github-json> -e event -t api-token -u user-key"
  opts.on('-tTOKEN', '--token=TOKEN', "Application API-token") {|o| options[:token] = o}
  opts.on('-uUSER', '--user=USER', "User/group key") {|u| options[:user] = u }
  opts.on('-eEVENT', '--event=EVENT', "The event (push, issues, etc)") {|o| options[:event] = o}
end.parse!

def valid_options? options
  failed = false
  unless options[:token]
    puts 'No API-token supplied (-t)'
    failed = true
  end
  unless options[:user]
    puts 'No user supplied (-u)'
    failed = true
  end
  unless options[:event]
    puts 'No event supplied (-e)'
    failed = true
  else
    # TODO: issue_comment, member, pull_request, repository and team_add
    valid_events = ['push', 'issues'].freeze
    unless valid_events.include? options[:event]
      puts options[:event] + ' is not a supported event. Supports ' + valid_events.to_s
      failed = true
    end
  end

  exit 1 if failed
end

def truncate s, length = MAX_URL_TITLE, ellipsis = ELLIPSIS
  if s.length > length
    s.to_s[0..length-ellipsis.bytesize].gsub(/[^\w]\w+\s*$/, ellipsis)
  else
    s
  end
end

def valid_api_keys? token, user
  if token.size != 30 || user.size != 30
    abort 'Token and/or user size is wrong. They should be 30 chars'
  end

  abort 'Wrong token format' unless token.match(/^([A-Za-z0-9]+|)$/)
  abort 'Wrong user format' unless user.match(/^([A-Za-z0-9]+|)$/)
end

def parse_issues(payload)
  issue = payload['issue']
  action = payload['action']
  ignore = ['unassigned', 'labeled', 'unlabeled']
  if ignore.include? action
    abort "Issue parsing: ignoring action '#{action}'"
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
  end.join "\n"

  url = p['compare']
  url_title = "Compare on GitHub"
  title = "#{pushee} pushed to #{branch} at #{repo}"
  {url: url, title: title, message: message, url_title: url_title}
end

abort "No GitHub-JSON supplied" unless ARGV[0]

valid_options? options
valid_api_keys? options[:token], options[:user]
begin
  payload = JSON.parse(ARGV[0])
rescue JSON::ParserError
  abort 'Invalid JSON supplied'
end

data = send "parse_#{options[:event]}", payload

push_url = URI.parse("https://api.pushover.net/1/messages.json")
req = Net::HTTP::Post.new(push_url.path)
req.set_form_data({
   :token => options[:token],
   :user => options[:user],
   :title => (truncate data[:title], MAX_TITLE),
   :message => (truncate data[:message], MAX_BODY),
   :url => data[:url],
   :url_title => (truncate data[:url_title], MAX_URL_TITLE)
})
# TODO: take time from GitHub. Allows resending of older messages

res = Net::HTTP.new(push_url.host, push_url.port)
res.use_ssl = true
res.verify_mode = OpenSSL::SSL::VERIFY_PEER
res.start {|http| puts http.request(req).body }
