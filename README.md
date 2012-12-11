

For our final project in the class, we envision a system that can take a large passage of 
text and extract the significant actions performed by people or organizations (i.e the “events”)
and infer a temporal ordering of those actions. A system with these capabilities would be useful 
for answering queries about event ordering and for summarizing large texts.
We plan to build a system that will recognize and tag events in text and construct a 
representation of the time information related to those events. 

The types of events our system 
will focus on recognizing are actions performed by people or organizations. We will identify 
events using part of speech tagging, entity tagging, and by filtering out extraneous words. We 
will then use entity tagging to identify absolute time entities (ex. Tuesday) and relative time 
entities (ex. before, after, next) that occur in sentences with events in them. One strategy for 
using these tags to order events is the following: (1) Identify events that are paired with exact 
times (2) Order events that use relative time entities to refer to other events (3) If an event 
in the text is not related to any other event and has no absolute time, we assume the event 
occurs after the previous event in the text since most prose is written chronologically. Using 
this strategy, we can build a timeline that uses the events with exact times as a baseline for the 
ordering.


The final system should be able to take input text and output the chronologically ordered 
events extracted from the text. After doing this processing, the system will also support queries 
about which of two events happened first, giving the exact time of each event, if available.