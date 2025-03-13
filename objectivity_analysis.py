from openai import OpenAI
import random

with open("openai_key.txt") as f:
    API_Key_From_File = f.read()[:-1]

client = OpenAI(
  api_key=API_Key_From_File
)

# Completely false text, should return a score of 0
# Sourced from The Onion, for testing only
example_parody = """
Nation's Educators Alarmed By Poorly Written Teen Suicide Notes
WASHINGTON, DC—At the group’s annual convention Sunday, members of the National Education Association called for the formation of a nationwide coalition of parents, teachers and political leaders to address a rapidly growing problem: the alarmingly low quality of teenage suicide notes across the U.S.
In the convention’s keynote address, U.S. Secretary of Education Richard Riley said America must renew its commitment to grammar, spelling and writing skills, calling the marked improvement of teen suicide prose “the nation’s number one educational priority.”

“Not three days ago I met with the parents of a young man who chose to take his own life,” Riley said. “I was shocked by what I saw: a note that read simply, ’Im gonna blo my head of.’ This sort of syntax is understandable coming from a first- or second-grader, but from a 17-year-old it is downright appalling,” Riley said. “What do you tell the parents in a situation like that? By all outward appearances, this seemed like a normal child. The poor parents had no idea their son’s writing skills were that poor.”

Addressing the assemblage of teachers, NEA president Cheryl Brodhagen described an “alarming erosion of grammar skills” among America’s teens, in whose suicide notes can be found double negatives, split infinitives, improper word usage and—in the worst cases—unnecessary use of the passive voice.

Calling the decision to take one’s life “one of the most important decisions a young student has to face,” Brodhagen said that to leave behind poorly written and misspelled suicide notes of the type found recently is “tragic beyond words” for the loved ones left behind to pick up the pieces.

“This one, for example,” said Brodhagen, holding up a suicide note from a 16-year-old Pawtucket, RI, girl, “is written in such shaky, uneven handwriting and is so badly blurred with some sort of wet stains and splotches that it’s virtually unreadable. In any decent classroom it would be considered entirely unacceptable.”

Brodhagen then related the story of another tragic suicide note, discovered at the feet of a 15-year-old St. Louis boy who had hanged himself.

“The boy’s mother opened the door to his room one morning to wake him up for school,” Brodhagen said, “and she screamed in horror at what she saw: Dangling, right there in front of her, was a participle.”
Also cause for concern among educators is the excessively “purple” prose of many teen suicide notes. Said Savannah, GA, ninth grade creative-writing teacher Ed Salmons: “I’m seeing overwrought, melodramatic, bathetic writing that demonstrates no grasp of subtlety or style. It’s really hard for me to take pretentious, self-indulgent suicide notes like these seriously as pieces of writing. It’s as if the author was just in love with the sound of his or her own voice.”

According to leading child psychologists, a suicidal teen’s failure to meet even the most basic standards of high-school-level composition may indicate the child has given up hope of ever having his or her written prose understood.

“These teens are desperately trying to express themselves, but all they can manage are sloppy, barely coherent phrases like ’Im usles’ and ’I hat myself,’” noted therapist Eli Wasserbaum said. “One Florida boy who recently shot himself in the head wrote, ’I cant talk to anyone about my problems.’ ’Cant’? Is he referring to the noun defined as ’the whining, singsong speech of beggars and thieves’? Somehow, I don’t think so. We’re talking about a serious inability to communicate here.”

Wasserbaum said that early detection and intervention is crucial. “My advice is this: If you know a teen who seems to be exhibiting the sort of low self-esteem and withdrawn alienation that often precedes suicidal behaviors, for God’s sake, get them into a one-on-one writing tutorial immediately. They’ve got to improve their communication skills now, before it’s too late,” he said.

The NEA is currently developing a 12-step plan to improve suicidal teens’ reading and writing skills, including extra homework for students deemed “at-risk” by counselors and tougher grading standards for teens who have attempted suicide on one or more occasions.

The proposal also calls for the creation of special ’suicidal-only’ after-school study halls to prevent depressed teens from engaging in extracurricular social activities with their peers, activities which may interfere with their studies and lead to greater erosion of basic grammar and spelling down the road.
"""

# Objective text, should return a score of 1
# Sourced from The Guardian, for testing only
example_objective= """
The UK population exceeded that of France for the first time on record, according to the Office for National Statistics (ONS).

The UK population is projected to reach 72.5 million by mid-2032, up nearly 5 million from 67.6 million in mid-2022, according to figures from the ONS.

ONS figures show the population was 68.3 million in mid-2023, surpassing France’s 68.2 million, a figure published by Insee, the French equivalent to the ONS.

The driver of the growth over the period was migration, with natural change – the difference between births and deaths – projected to be about zero, according to the ONS.

International migration for the period is expected to be 4.9 million over the 10 years. This has been revised upwards from the previous projection of 4.5 million.

The prime minister’s official spokesperson said Keir Starmer wants to bring down “staggeringly high levels” of migration but will not set “arbitrary” caps.

“We’re going to publish a white paper to set out a comprehensive plan to end these staggeringly high migration numbers,” said the spokesperson.

“As the prime minister has previously said, we had a supposed cap in place before and it didn’t have any meaningful impact on reducing immigration.

“So he doesn’t think that setting an arbitrary cap, as previous governments have done, is the best way forward in terms of significantly reducing migration.”

The number of births and deaths across the period is projected to be almost identical, with about 6.8 million births offset by 6.8 million deaths.

While births are projected to increase slightly, deaths are also projected to rise due to the relatively large number of people reaching older ages who were born during the “baby boom” after the second world war.

The level of net migration to the UK is projected to average 340,000 per year from mid-2028 onwards, lower than current levels.
"""

to_be_analysed = random.chocie([example_parody, example_objective])
if to_be_analysed == example_objective:
    print('Objective text test')
else:
    print('False text test')
print()

prompt = ("""
You will be provided with the text from a news article, using your expertise in media literacy you are to analyse the level of the objectivity in the text.
On a scale of 0-1 rate the objectivity in the text, based on how true the statements made are (you should look them up), 0 being completely false and 1 being completely accurate, giving your answer in decimal format to 1 decimal place.
Return your answer in json format.ii

It is extremely important that you rate the objectivity as accurate as possible and return your rating in the correct format as the success of the company depends on it.

"""
          + "The text to be analysed is:" + to_be_analysed)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": prompt}
  ]
)

response = completion.choices[0].message.content
print(response)