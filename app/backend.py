import urllib.request
from html.parser import HTMLParser
import json

class Quiz:
    @staticmethod
    def url_to_quiz(url):
        fp = urllib.request.urlopen(url)
        rawb = fp.read()
        raw = rawb.decode("utf8")
        fp.close()

        class MyHTMLParser(HTMLParser):
            def __init__(self, result):
                HTMLParser.__init__(self)
                self.record_title = 1
                self.result = result
                self.record_data = False
                self.script = False

            def handle_starttag(self, tag, attributes):
                if tag == 'title' and self.record_title == 1:
                    self.record_title += 1
                    return

                if tag == 'div':
                    for name, value in attributes:
                        if name == 'data-module' and (
                                                value == 'quiz-personality' or value == 'quiz-standard' or value == 'quiz-poll' or value == "quiz-checklist"):
                            self.result["quiz type"] = value
                            self.record_data += True

                if tag == 'script':
                    self.script = True

            def handle_endtag(self, tag):
                if tag == 'title':
                    self.record_title -= 2

                if tag == 'script':
                    self.script = False

            def handle_data(self, data):
                if self.record_title == 2:
                    self.result['title'] = data
                    return

                if self.record_data and self.script:
                    self.result['data'].append(data)
                    self.record_data = False

        parse_data = dict()
        parse_data['data'] = []
        parser = MyHTMLParser(parse_data)
        parser.feed(raw)

        json_data = parse_data['data'][0]
        python_obj = json.loads(json_data)
        python_obj = python_obj['subbuzz']
        type = parse_data['quiz type']

        if type == "quiz-personality":
            q = Personality_Quiz(python_obj, parse_data['title'])
        elif type == "quiz-poll":
            q = Poll_Quiz(parse_data['data'], parse_data['title'])
        elif type == "quiz-standard":
            q = Standard_Quiz(python_obj, parse_data['title'])
        elif type == "quiz-checklist":
            q = Checklist_Quiz(python_obj, parse_data['title'])

        return q

    def __init__(self, python_obj, title):
        self.title = title
        self.raw_questions = python_obj['questions']
        self.raw_results = python_obj['results']
        self.tlength = len(python_obj['results'])
        self.generate_questions()
        self.generate_results()
        self.generate_top_row()

    def get_title(self):
        return self.title

    def get_results(self):
        return self.results

    def get_questions(self):
        return self.questions

    def generate_top_row(self):
        pass

    def get_top_row(self):
        return self.top_row


class Personality_Quiz(Quiz):
    def __init__(self, python_obj, title):
        self.tlength = len(python_obj['results'])
        super().__init__(python_obj, title)

    def generate_top_row(self):
        self.top_row = [r[0] for r in self.results]

    def generate_results(self):
        results_data = self.raw_results
        self.results = [(option['header'], option['description'], option['data_src']) for option in results_data]

    def generate_questions(self):
        questions_data = self.raw_questions
        rv = []
        for option in questions_data:
            try:
                text = option['header'] or option['image_text']
            except KeyError:
                text = ""
            image = ""
            if option['image'] and not 'image_text' in option:
                image = option['image']
            answers = [("", "") * 2] * self.tlength
            for a in option['answers']:
                try:
                    atext = a['header'] or a['image_text']
                except KeyError:
                    atext = ""
                aimage = ""
                if a['image'] and not 'image_text' in a:
                    aimage = a['image']
                answers[a['personality_index']] = (atext, aimage)

            rv.append((text, option['description'], image, answers))
        self.questions = rv


class Standard_Quiz(Quiz):
    def __init__(self, python_obj, title):
        super().__init__(python_obj, title)

    def generate_top_row(self):
        self.top_row = ["Correct"]

    def generate_questions(self):
        questions_data = self.raw_questions
        rv = []
        for option in questions_data:
            try:
                text = option['header'] or option['image_text']
            except KeyError:
                text = ""
            image = ""
            if option['image'] and not 'image_text' in option:
                image = option['image']
            answers = [("", "") * 2]
            for a in option['answers']:
                try:
                    atext = a['header'] or a['image_text']
                except KeyError:
                    atext = ""
                aimage = ""
                if a['image'] and not 'image_text' in a:
                    aimage = a['image']
                if a["correct"]:
                    answers[0] = (atext, aimage)
                else:
                    answers.append((atext, aimage))
            rv.append((text, option['description'], image, answers))

            if option['has_reveal']:
                a = option['reveal']
                try:
                    atext = a['header'] or a['image_text']
                except KeyError:
                    atext = ""
                aimage = ""
                if a['image'] and not 'image_text' in a:
                    aimage = a['image']
                rv.append((atext, a['description'], aimage, []))

        self.questions = rv

    def generate_results(self):
        results_data = self.raw_results
        results = []
        range_start = 0
        results_data.sort(key=lambda x: int(x['range_end']))
        for option in results_data:
            if 'range_start' in option:
                range_start = option['range_start']
            results.append(("(" + str(range_start) + " - " + option['range_end'] + ") " + option['header'],
                            option['description'], option['data_src']))
            range_start = option['range_end']
        self.results = results


class Poll_Quiz(Quiz):
    def __init__(self, parse_data, title):
        self.title = title

        self.raw_questions = []
        self.raw_results = []

        for json_data in parse_data:
            python_obj = json.loads(json_data)
            python_obj = python_obj['subbuzz']
            self.raw_questions.append(python_obj['questions'])
            self.raw_results.append(python_obj['results'])

        self.generate_questions()
        self.generate_results()
        self.generate_top_row()

    def generate_top_row(self):
        self.top_row = []

    def generate_results(self):
        results_data = self.raw_results[0]
        results = []
        range_start = 0
        for option in results_data:
            pass
            # results.append(("("+str(range_start)+" - " +option['range_end']+") "+option['header'], option['description'], option['data_src']))
            # range_start=option['range_end']
        self.results = results

    def generate_questions(self):
        rv = []
        for questions_data in self.raw_questions:
            option = questions_data[0]
            try:
                text = option['header'] or option['image_text']
            except KeyError:
                text = ""
            image = ""
            if option['image'] and not 'image_text' in option:
                image = option['image']
            answers = []
            for a in option['answers']:
                try:
                    atext = a['header'] or a['image_text']
                except KeyError:
                    atext = ""
                aimage = ""
                if a['image'] and not 'image_text' in a:
                    aimage = a['image']
                answers.append((atext, aimage))

            rv.append((text, option['description'], image, answers))
        self.questions = rv


class Checklist_Quiz(Quiz):
    def __init__(self, python_obj, title):
        super().__init__(python_obj, title)

    def generate_top_row(self):
        self.top_row = ["Correct"]

    def generate_questions(self):
        questions_data = self.raw_questions
        rv = []
        for option in questions_data:
            try:
                text = option['header'] or option['image_text']
            except KeyError:
                text = ""
            image = ""
            if option['image'] and not 'image_text' in option:
                image = option['image']
            answers = []
            for a in option['answers']:
                try:
                    atext = a['header'] or a['image_text']
                except KeyError:
                    atext = ""
                aimage = ""
                if a['image'] and not 'image_text' in a:
                    aimage = a['image']
                answers.append((atext, aimage))
            rv.append((text, option['description'], image, answers))

            if option['has_reveal']:
                a = option['reveal']
                try:
                    atext = a['header'] or a['image_text']
                except KeyError:
                    atext = ""
                aimage = ""
                if a['image'] and not 'image_text' in a:
                    aimage = a['image']
                rv.append((atext, a['description'], aimage, []))

        self.questions = rv

    def generate_results(self):
        results_data = self.raw_results
        results = []
        range_start = 0
        results_data.sort(key=lambda x: int(x['range_end']))
        for option in results_data:
            if 'range_start' in option:
                range_start = option['range_start']
            results.append(("(" + str(range_start) + " - " + option['range_end'] + ") " + option['header'],
                            option['description'], option['data_src']))
            range_start = option['range_end']
        self.results = results
