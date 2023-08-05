# Copyright (C) 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of LAVA Kernel CI Views.
#
# LAVA Kernel CI Views is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License version 3 as
# published by the Free Software Foundation
#
# LAVA Kernel CI Views is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Kernel CI Views.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict, namedtuple
import contextlib
import datetime
import json

from django.core.urlresolvers import reverse
from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response

from dashboard_app.models import DataView, TestResult


DAY_DELTA = datetime.timedelta(days=1)
WEEK_DELTA = datetime.timedelta(days=7)

def fetchnamed(cursor):
    class cls(object):
        pass
    names = ' '.join(col[0] for col in cursor.description)
    typ = namedtuple('result', names)
    for row in cursor.fetchall():
        yield typ(*row)


index_sql = """
select softwaresource.branch_url as git_url,
       softwaresource.branch_revision as git_commit_id,
       coalesce(namedattribute_git_describe.value, softwaresource.branch_revision) as git_describe,
       coalesce(namedattribute_git_log_info.value, softwaresource.branch_revision) as git_log_info,
       namedattribute_gitweb_url.value as gitweb_url,
       softwaresource.commit_timestamp as commit_timestamp,
       testrun.analyzer_assigned_date as build_date,
       namedattribute_kernelconfig.value as config,
       testresult.result as result,
       namedattribute_kernelbuild_url.value as build_url,
       bundle.content_sha1 as bundle_sha1
  from dashboard_app_bundlestream as bundlestream,
       dashboard_app_bundle as bundle,
       dashboard_app_testresult as testresult,
       dashboard_app_testrun as testrun
inner join dashboard_app_namedattribute AS namedattribute_kernelconfig
        on (namedattribute_kernelconfig.object_id = testrun.id
            and namedattribute_kernelconfig.name = 'kernel.config'
            and namedattribute_kernelconfig.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
inner join dashboard_app_namedattribute AS namedattribute_kernelbuild_url
        on (namedattribute_kernelbuild_url.object_id = testrun.id
            and namedattribute_kernelbuild_url.name = 'kernel.build_url'
            and namedattribute_kernelbuild_url.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_git_describe
        on (namedattribute_git_describe.object_id = testrun.id
            and namedattribute_git_describe.name = 'kernel.git_describe_info'
            and namedattribute_git_describe.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_git_log_info
        on (namedattribute_git_log_info.object_id = testrun.id
            and namedattribute_git_log_info.name = 'kernel.git_log_info'
            and namedattribute_git_log_info.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
left outer join dashboard_app_namedattribute as namedattribute_gitweb_url
        on (namedattribute_gitweb_url.object_id = testrun.id
            and namedattribute_gitweb_url.name = 'kernel.gitweb_url'
            and namedattribute_gitweb_url.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            ),
       dashboard_app_softwaresource as softwaresource,
       dashboard_app_testrun_sources as tr_ss_link
 where bundle.bundle_stream_id = bundlestream.id
   and testrun.bundle_id = bundle.id
   and softwaresource.id = tr_ss_link.softwaresource_id
   and testrun.id = tr_ss_link.testrun_id
   and bundlestream.slug like 'ci-linux%%-build'
   and testresult.test_run_id = testrun.id
   and %s < testrun.analyzer_assigned_date and testrun.analyzer_assigned_date < %s
"""

find_builds_sql = """
select testresult.result as result,
       namedattribute_kernelbuild_url.value as build_url,
       namedattribute_targethostname.value as targethostname,
       testcase.test_case_id as test_case_id,
       bundle.content_sha1 as bundle_sha1
  from dashboard_app_bundlestream as bundlestream,
       dashboard_app_bundle as bundle,
       dashboard_app_testresult as testresult,
       dashboard_app_testcase as testcase,
       dashboard_app_testrun as testrun
inner join dashboard_app_namedattribute AS namedattribute_targethostname
        on (namedattribute_targethostname.object_id = testrun.id
            and namedattribute_targethostname.name = 'target.hostname'
            and namedattribute_targethostname.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
inner join dashboard_app_namedattribute AS namedattribute_kernelbuild_url
        on (namedattribute_kernelbuild_url.object_id = testrun.id
            and namedattribute_kernelbuild_url.name = 'kernel.build_url'
            and namedattribute_kernelbuild_url.content_type_id = (
                select django_content_type.id from django_content_type
                where app_label = 'dashboard_app' and model='testrun')
            )
 where bundle.bundle_stream_id = bundlestream.id
   and testrun.bundle_id = bundle.id
   and bundlestream.slug like 'ci-linux%%'
   and testresult.test_run_id = testrun.id
   and testresult.test_case_id = testcase.id
   and namedattribute_kernelbuild_url.value = ANY(%s)
"""

class Test(object):
    def __init__(self, board_class, sha1, build):
        self._board_class = board_class
        self.sha1 = sha1
        self.build = build
        self.results = defaultdict(set)
    @property
    def passes(self):
        return len(self.results[TestResult.RESULT_PASS])
    @property
    def fails(self):
        return len(self.results[TestResult.RESULT_FAIL])
    def json_ready(self):
        if self.fails > 0:
            result = 'fail'
        else:
            result = 'pass'
        if self.prev:
            pass_to_fail = self.results[TestResult.RESULT_FAIL] & \
                           self.prev.results[TestResult.RESULT_PASS]
            pass_to_fail = sorted(pass_to_fail)
            fail_to_pass = self.results[TestResult.RESULT_PASS] & \
                           self.prev.results[TestResult.RESULT_FAIL]
            fail_to_pass = sorted(fail_to_pass)
        else:
            pass_to_fail = []
            fail_to_pass = []
        return {
            'board_class': self._board_class,
            'result': result,
            'passes': self.passes,
            'fails': self.fails,
            'test_count': self.passes + self.fails,
            'sha1': self.sha1,
            'pass_to_fail': len(pass_to_fail),
            'fail_to_pass': len(fail_to_pass),
            }


class Build(object):
    def __init__(self, config, result, sha1, commit):
        self._config = config
        self._result = result
        self._tests = {}
        self.sha1 = sha1
        self.commit = commit
    @property
    def tests(self):
        return self._tests.values()
    def json_ready(self):
        tests = [test.json_ready()
                 for (board_class, test) in sorted(self._tests.iteritems())]
        if self._result:
            result = 'fail'
        else:
            result = 'pass'
        return {
            'config': self._config,
            'result': result,
            'tests': tests,
            'sha1': self.sha1,
            }
    def add_test(self, board_class, test_case, result, sha1):
        if board_class in self._tests:
            test = self._tests[board_class]
        else:
            test = self._tests[board_class] = Test(board_class, sha1, self)
        test.results[result].add(test_case)
        return test
    def find_test(self, board_class):
        return self._tests.get(board_class)


class Commit(object):
    def __init__(self, sha1, commit_timestamp, describe, log_info, gitweb_url, tree):
        self.sha1 = sha1
        self.commit_timestamp = commit_timestamp
        self.describe = describe
        self._builds = []
        self.log_info = log_info
        self.gitweb_url = gitweb_url
        self.tree = tree
    def add_build(self, config, result, sha1):
        build = Build(config, result, sha1, self)
        self.tree.day.daycollection._configs.add(config)
        self._builds.append(build)
        return build
    def find_builds(self, config):
        for build in self._builds:
            if build._config == config:
                yield build
    @property
    def builds(self):
        return list(self._builds)
    def json_ready(self):
        builds = [build.json_ready() for build in self._builds]
        def sort_key(build):
            has_test = len(build['tests']) > 0
            if has_test:
                board_class = build['tests'][0]['board_class']
            else:
                board_class = None
            return (-has_test, build['config'], board_class)
        builds.sort(key=sort_key)
        for build in builds:
            build['width'] = (100.0 - len(builds) + 1)/len(builds)
        if self.prev:
            prev = self.prev.sha1
        else:
            prev = None
        commit_url = shortlog_url = None
        if self.gitweb_url:
            if 'github' in self.gitweb_url:
                base_url = self.gitweb_url
                if base_url.endswith('.git'):
                    base_url = base_url[:-len('.git')]
                commit_url = base_url + '/commit/' + self.sha1
            else:
                commit_url = self.gitweb_url + ';a=commit;h=' + self.sha1
                if self.prev:
                    shortlog_url = '%s;a=shortlog;h=%s;hp=%s' % (
                        self.gitweb_url, self.sha1, self.prev.sha1)
        return {
            'sha1': self.sha1,
            'describe': self.describe,
            'builds': builds,
            'test_count': sum(len(build['tests']) for build in builds),
            'prev': prev,
            'log_info': self.log_info,
            'commit_url': commit_url,
            'shortlog_url': shortlog_url,
            }


class Tree(object):
    def __init__(self, git_url, index, day):
        self._git_url = git_url
        self._commits = {}
        self.day = day
        self.index = index
    def get_commit(self, sha1, commit_timestamp, describe, log_info, gitweb_url):
        if sha1 in self._commits:
            # XXX if self._commits[sha1].commit_timestamp != commit_timestamp ...
            return self._commits[sha1]
        else:
            commit_obj = self._commits[sha1] = Commit(
                sha1, commit_timestamp, describe, log_info, gitweb_url, self)
            return commit_obj
    @property
    def commits(self):
        return self._commits.values()
    def json_ready(self):
        def key(commit):
            return commit.commit_timestamp
        commits = self._commits.values()
        commits.sort(key=key)
        commits.reverse()
        commits = [commit.json_ready() for commit in commits]
        return {
            'name': self._git_url,
            'commits': commits,
            'test_count': sum(commit['test_count'] for commit in commits),
            'build_count': sum(len(commit['builds']) for commit in commits),
            'index': self.index,
            }


class Day(object):
    def __init__(self, day, daycollection):
        self._day = day
        self._trees = {}
        self.daycollection = daycollection
    def get_tree(self, git_url, index):
        if git_url in self._trees:
            return self._trees[git_url]
        else:
            tree_obj = self._trees[git_url] = Tree(git_url, index, self)
            return tree_obj
    @property
    def trees(self):
        return self._trees.values()
    def json_ready(self):
        # XXX how do we order trees?
        trees = [tree.json_ready() for tree in self._trees.values()]
        for tree in trees:
            tree['width'] = (100.0 - len(trees) + 1)/len(trees)
        trees.sort(key=lambda tree:tree['name'])
        return {
            'date': self._day.strftime('%A %B %d %Y'),
            'trees': trees,
            'build_count': sum(tree['build_count'] for tree in trees),
            'test_count': sum(tree['test_count'] for tree in trees),
            'tree_count': len([tree for tree in trees if tree['build_count'] > 0]),
            }


class DayCollection(object):
    def __init__(self, start, finish):
        self.start = start
        self.finish = finish
        self._days = {}
        # We create a Day object for every day we're interested in, plus one
        # day older so that we can find the previous build for the last row of
        # builds displayed.  This isn't quite enough, because the previous
        # build might have been more than one day before the last one
        # displayed, but for now it's a reasonable hack.
        d = start - DAY_DELTA
        while d < finish:
            self._days[d] = Day(d, self)
            d += DAY_DELTA
        self._board_classes = set()
        self._configs = set()
        self._urls_to_builds = {}
        self._tree2index = {}
        self.all_trees = set()

    def get_day(self, datestamp):
        day = datestamp.date()
        return self._days[day]

    def add_build(self, build_results):
        day = self.get_day(build_results.build_date)
        git_url = build_results.git_url
        if git_url not in self._tree2index:
            self._tree2index[git_url] = len(self._tree2index)
        tree = day.get_tree(git_url, self._tree2index[git_url])
        self.all_trees.add(tree)
        print repr(build_results.gitweb_url)
        commit = tree.get_commit(
            build_results.git_commit_id, build_results.commit_timestamp,
            build_results.git_describe, build_results.git_log_info, build_results.gitweb_url)
        config = build_results.config
        if config.endswith('_defconfig'):
            config = config[:-len('_defconfig')]
        self._configs.add(config)
        build = commit.add_build(
            config, build_results.result, build_results.bundle_sha1)
        build_url = build_results.build_url
        if build_url != 'unknown':
            self._urls_to_builds[build_url] = build

    def add_test(self, test_result):
        board_class = test_result.targethostname.strip('0123456789')
        self._board_classes.add(board_class)
        self._urls_to_builds[test_result.build_url].add_test(
            board_class, test_result.test_case_id, test_result.result,
            test_result.bundle_sha1)

    def compute_prevs(self):
        # tree_commits maps git urls to Commit objects in the order they were
        # built.  Notice that it's not only possibly but likely that there
        # will be more than one Commit for a given git_commit_id (and hence
        # commit_timestamp) because we run builds daily even if the tip hasn't
        # changed.

        tree_commits = defaultdict(list)
        for day in sorted(self.days, key=lambda day:day._day):
            for tree in day.trees:
                commits = tree.commits
                commits.sort(key=lambda commit: commit.commit_timestamp)
                tree_commits[tree._git_url].extend(commits)
        for commits_list in tree_commits.values():
            if commits_list:
                commits_list.sort(key=lambda commit: commit.commit_timestamp)
                commits_list[0].prev = None
                for i in range(1, len(commits_list)):
                    commits_list[i].prev = commits_list[i-1]

        for day in self.days:
            for tree in day.trees:
                for commit in tree.commits:
                    for build in commit.builds:
                        for test in build.tests:
                            test.prev = None
                            prev_commit = test.build.commit.prev
                            while prev_commit is not None:
                                for prev_build in prev_commit.find_builds(test.build._config):
                                    prev_test = prev_build.find_test(test._board_class)
                                    if prev_test:
                                        test.prev = prev_test
                                        break
                                if test.prev:
                                    break
                                prev_commit = prev_commit.prev

    def evaluate(self):
        connection = DataView.get_connection()
        with contextlib.closing(connection.cursor()) as cursor:
            cursor.execute(index_sql, (self.start - DAY_DELTA, self.finish))

            for build_result in fetchnamed(cursor):
                self.add_build(build_result)

            cursor.execute(find_builds_sql, (self._urls_to_builds.keys(),))

            for test_result in fetchnamed(cursor):
                self.add_test(test_result
)
        self.compute_prevs()

        self.fill_in_missing_trees()

    def fill_in_missing_trees(self):
        for day in self.days:
            missing_trees = self.all_trees - set(day.trees)
            for tree in missing_trees:
                day.get_tree(tree._git_url, self._tree2index[tree._git_url])

    @property
    def days(self):
        return self._days.values()

    def json_ready(self):
        def key(day_obj):
            return day_obj._day
        day_objs = self._days.values()
        day_objs.sort(key=key)
        day_objs.reverse()
        # Remove the extra day (see __init__ for the comment about this).
        del day_objs[-1]
        trees = []
        for url, index in sorted(self._tree2index.items()):
            trees.append({
                'url': url,
                'index': index,
                'width': (100.0 - len(self._tree2index) + 1)/len(self._tree2index)
                })
        return {
            'days': [day_obj.json_ready() for day_obj in day_objs],
            'trees': trees,
            }


class DateRange(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)


def index(request):

    form = DateRange(request.GET)
    form.is_valid()
    start = form.cleaned_data['start']
    if start is None:
        start = datetime.date.today() - WEEK_DELTA + DAY_DELTA

    end = form.cleaned_data['end']
    if end is None:
        end = datetime.date.today() + DAY_DELTA

    day_collection = DayCollection(start, end)

    day_collection.evaluate()

    link_prefix = reverse(
        'dashboard_app.views.redirect_to_bundle',
        kwargs={'content_sha1':'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'}
        ).replace('aaaaaaaaaaaaaaaaaaaaaaaaaaaa/', '')

    data = day_collection.json_ready()
    newer_results_link = None
    if end <= datetime.date.today() + DAY_DELTA:
        newer_start = end
        newer_end = max(
            newer_start + WEEK_DELTA, datetime.date.today())
        newer_results_link = (
            reverse(index) + '?start=' + newer_start.strftime('%Y-%m-%d') +
            '&end=' + newer_end.strftime('%Y-%m-%d'))
    older_end = start
    older_start = older_end - WEEK_DELTA
    older_results_link = (
        reverse(index) + '?start=' + older_start.strftime('%Y-%m-%d') +
        '&end=' + older_end.strftime('%Y-%m-%d'))
    return render_to_response(
        "lava_kernel_ci_views_app/index.html",
        {
            'data': data,
            'link_prefix': link_prefix,
            'board_classes': sorted(day_collection._board_classes),
            'configs': sorted(day_collection._configs),
            'trees': sorted(day_collection._tree2index.items()),
            'newer_results_link': newer_results_link,
            'older_results_link': older_results_link,
        }, RequestContext(request))

