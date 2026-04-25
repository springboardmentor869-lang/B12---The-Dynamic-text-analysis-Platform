# Converted Document

MODULE 1 - Introduction to Software Testing

TRACE KTU

Bug, Fault & Failure

• A person makes an Error

• That creates a fault in software

• That can cause a failure in operation

• Error : An error is a human action that produces the incorrect result that

results in a fault.

• Bug : The presence of error at the time of execution of the software.

• Fault : State of software caused by an error.

• Failure : Deviation of the software from its expected result. It is an event.

• Defect :A defect is an error or a bug, in the application which is created. A

programmer while designing and building the software can make mistakes

or error. These mistakes or errors mean that there are flaws in the

software. These are called defects.

TRACE KTU

TRACE KTU

TRACE KTU

Why do defects occur in software?

Software is written by human beings

􀂾

Who know something, but not everything

􀂾

Who have skills, but aren’t perfect

􀂾

Who don’t usually use rigorous methods

􀂾

Who do make mistakes (errors)

Under increasing pressure to deliver to strict deadlines

􀂾

No time to check, assumptions may be wrong

􀂾

Systems may be incomplete

Software is complex, abstract and invisible

􀂾

Hard to understand

􀂾

Hard to see if it is complete or working correctly

􀂾

No one person can fully understand large systems

􀂾

Numerous external interfaces and dependencies

TRACE KTU

Sources of defects

Education

􀂾

Developers does not understand well enough what he or she is doing

􀂾

Lack of proper education leads to errors in specification,design, coding,

and testing

Communication

􀂾

Developers do not know enough

􀂾

Information does not reach all stakeholders

􀂾

Information is lost

Oversight

􀂾

Omitting to do necessary things

Transcription

􀂾

Developer knows what to do but simply makes a mistake

Process

􀂾

Process is not applicable for the actual situation

􀂾

Process places restrictions that cause errors

TRACE KTU

Objective of testing

• To find defects before they cause a production system to fail.

• To bring the tested software, after correction of the identified defects

and retesting, to an acceptable level of quality.

• To perform the required tests efficiently and effectively, within the

limits budgetary and scheduling limitation.

• To compile a record of software errors for use in error prevention (by

corrective and preventive actions)

TRACE KTU

TRACE KTU

TRACE KTU

TRACE KTU

Software Quality Concept

Quality : Quality means consistently meeting customer needs in

terms of requirement, Cost and delivery schedule.

Quality of s/w is reasonably bug free, delivered on time and

within budget, meets requirements and exceptions and is

maintainableTRACE KTU

Software Quality Concept

●Quality Control: “All defined work products and Measurable

Specifications”  are compared with the output of each

process.

●Quality control focuses on operational technique and activities

used to fulfill and verify requirement of quality.

●- S/w quality involves – Series of inspection, reviews, and test

used through out the s/w process.

TRACE KTU

Quality Assurance (QA): consist of Auditing and reporting

procedure. Which are used to provide necessary data to

management. In order to make decision.

●Goal of Quality Assurance is to provide adequate

confidence that a product or services is of the and quality

expected by the customer.

●If the data provided through quality assurance identify

problems, then it is management’s responsibility to address

the problems & apply the necessary resources to resole

quality issues.

TRACE KTU

TRACE KTU

TRACE KTU

TRACE KTU

TRACE KTU

TRACE KTU

What is Verification?

• Definition : The process of evaluating software to determine whether the

products of a given development phase satisfy the conditions imposed at

the start of that phase.

• Verification is a static practice of verifying documents, design, code and

program. It includes all the activities associated with producing high quality

software: inspection, design analysis and specification analysis. It is a

relatively objective process.

• Verification will help to determine whether the software is of high quality,

but it will not ensure that the system is useful. Verification is concerned

with whether the system is well-engineered and error-free.

• Methods of Verification : Static Testing

• Walkthrough

• Inspection

• Review

TRACE KTU

What is Validation?

• Definition: The process of evaluating software during or at the end of

the development process to determine whether it satisfies specified

requirements.

• Validation is the process of evaluating the final product to check

whether the software meets the customer expectations and

requirements. It is a dynamic mechanism of validating and testing the

actual product.

• Methods of Validation : Dynamic Testing

• Testing

• End Users

TRACE KTU

Verification

Validation

1. Verification is a static practice of verifying documents,

design, code and program.

1. Validation is a dynamic mechanism of validating and

testing the actual product.

2. It does not involve executing the code.

2. It always involves executing the code.

3. It is human based checking of documents and files.

3. It is computer based execution of program.

4. Verification uses methods like inspections, reviews,

walkthroughs, and Desk-checking etc.

4. Validation uses methods like black box

(functional) testing, gray box testing, and white box

(structural) testing etc.

5. Verification is to check whether the software conforms

to specifications.

5. Validation is to check whether software meets the

customer expectations and requirements.

6. It can catch errors that validation cannot catch. It is low

level exercise.

6. It can catch errors that verification cannot catch. It is High

Level Exercise.

7. Target is requirements specification, application and

software architecture, high level, complete design, and

database design etc.

7. Target is actual product-a unit, a module, a bent of

integrated modules, and effective final product.

8. Verification is done by QA team to ensure that the

software is as per the specifications in the SRS document.

8. Validation is carried out with the involvement of testing

team.

9. It generally comes first-done before validation.

9. It generally follows after verification.

TRACE KTU

TRACE KTU

Coverage criteria are adequacy measures to qualify if a test objective is

satisfied when executing test cases on a system under test.

Coverage criteria are established to estimate the quality of test cases, and criteria

combinations are considered in software testing.

Coverage Criteria

TRACE KTU

Levels Of Testing

TRACE KTU

Unit Testing

• Unit Testing is a level of software testing where individual units/

components of a software are tested. The purpose is to validate that

each unit of the software performs as designed.

• Unit Testing is the first level of testing and is performed prior

to Integration Testing.

• A unit is the smallest testable part of software. It usually has one or

a few inputs and usually a single output.

• It is executed by the Developer.

• Unit Testing is performed by using the White Box Testing method

• Example: - A function, method, Loop or statement in program is

working fine.

TRACE KTU

TRACE KTU

Drivers

• Drivers are used in bottom-up integration testing approach.

• It can simulate the behavior of upper-level module that is not integrated yet.

• Drivers modules act as the temporary replacement of module and act as the

actual products.

• Drivers are also used for interact with external system and usually complex than

stubs.

• Driver: Calls the Module to be tested.

Now suppose you have modules B and C ready but module A which calls functions

from module B and C is not ready so developer will write a dummy piece of code

for module A which will return values to module B and C. This dummy piece of

code is known as driver.

TRACE KTU

Stubs

• Stubs are used in top down integration testing.

• It can simulate the behavior of lower-level module that are not integrated.

• They are act as a temporary replacement of module and provide same output as

actual product.

• When needs to intact with external system then also stubs are used.

• Stub: Is called by the Module under Test.

Assume you have 3 modules, Module A, Module B and module C. Module A is

ready and we need to test it, but module A calls functions from Module B and

C which are not ready, so developer will write a dummy module which

simulates B and C and returns values to module A. This dummy module code

is known as stub.

TRACE KTU

Stub

Driver

Type

Dummy codes

Dummy codes

Description

Routines that don’t actually do

anything except declare themselves

and the parameters they accept. The

rest of the code can then take these

parameters and use them as inputs

Routines that don’t actually do

anything except declare themselves

and the parameters they accept. The

rest of the code can then take these

parameters and use them as inputs

Used in

Top Down Integration

Bottom Up Integration

Purpose

To allow testing of the upper levels

of the code, when the lower levels of

the code are not yet developed.

To allow testing of the lower levels of

the code, when the upper levels of

the code are not yet developed.

TRACE KTU

Benefits

• Unit testing increases confidence in changing/ maintaining code. If

good unit tests are written and if they are run every time any code is

changed, we will be able to promptly catch any defects introduced

due to the change.

• Codes are more reusable.

• Development is faster.

• The cost of fixing a defect detected during unit testing is lesser in

comparison to that of defects detected at higher levels.

• Debugging is easy.

TRACE KTU

Integration Testing

• Integration Testing is a level of software testing where

individual units are combined and tested as a group.

• In integration Testing, individual software modules are

integrated logically and tested as a group.

• Integration testing tests integration or interfaces between

components, interactions to different parts of the system

such as an operating system, file system and hardware or

interfaces between systems.

• As displayed in the image below when two different

modules ‘Module A’ and ‘Module B’ are integrated then

the integration testing is done.

TRACE KTU

Integration Testing Approaches

TRACE KTU

Big Bang integration testing

• In Big Bang integration testing all components or modules

are integrated simultaneously, after which everything is

tested as a whole. As per the below image all the modules

from ‘Module 1’ to ‘Module 6’ are integrated

simultaneously then the testing is carried out.

TRACE KTU

Pros And Cons

• Convenient for small systems.

• Fault Localization is difficult.

• Since all modules are tested at once, high risk critical

modules are not isolated and tested on priority.

• Since the integration testing can commence only after "all"

the modules are designed, testing team will have less time

for execution in the testing phase.

TRACE KTU

Incremental Approach:

• In this approach, testing is done by joining two or more modules that

are logically related. Then the other related modules are added and

tested for the proper functioning. Process continues until all of the

modules are joined and tested successfully.

• This process is carried out by using dummy programs called Stubs and

Drivers. Stubs and Drivers do not implement the entire programming

logic of the software module but just simulate data communication

with the calling module.

• Stub: Is called by the Module under Test.

• Driver: Calls the Module to be tested.

TRACE KTU

Bottom up Integration

• In the bottom up strategy, each module at lower levels is

tested with higher modules until all modules are tested.

• It takes help of Drivers for testing

TRACE KTU

Advantages:

•Fault localization is easier.

•No time is wasted waiting for all modules to be

developed unlike Big-bang approach

Disadvantages:

•Critical modules (at the top level of software

architecture) which control the flow of application

are tested last and may be prone to defects.

•Early prototype is not possible

TRACE KTU

Top down Integration:

• In Top to down approach, testing takes place from top to

down following the control flow of the software system.

• Takes help of stubs for testing.

TRACE KTU

Advantages:

•Fault Localization is easier.

•Possibility to obtain an early

prototype.

•Critical Modules are tested on

priority; major design flaws could be

found and fixed first.

Disadvantages:

•Needs many Stubs.

•Modules at lower level are tested

inadequately.

TRACE KTU

Unit Testing

Integration Testing

Unit testing is a type of testing to

check if the small piece of code is

doing what it is suppose to do.

Integration testing is a type of

testing to check if different pieces of

the modules are working together.

Unit testing checks a single

component of an application.

The behavior of integration

modules is considered in the

Integration testing.

The scope of Unit testing is

narrow, it covers the Unit or

small piece of code under test.

Th

f

hil

iti

it

The scope of Integration testing is

wide, it covers the whole

application under test and it

TRACE KTU

System Testing

TRACE KTU

• The process of testing of an integrated hardware and software

system to verify that the system meets its specified requirements.

• It is performed when integration testing is completed.

• It is mainly a black box type testing. This testing evaluates working of

the system from a user point of view, with the help of specification

document. It does not require any internal knowledge of system like

design or structure of the code.

• It contains functional and non-functional areas of

application/product.

• System testing is performed in the context of a System Requirement

Specification (SRS) and/or a Functional Requirement Specifications

(FRS). It is the final test to verify that the product to be delivered

meets the specifications mentioned in the requirement document. It

should investigate both functional and non-functional

requirements.

TRACE KTU

• It mainly focuses on following:

External interfaces

complex functionalities

Security

Recovery

Performance

Operator and user’s smooth interaction with system

Documentation

Usability

Load / Stress

TRACE KTU

Performance Testing

• Performance Testing is a type of testing to ensure software

applications will perform well under their expected workload.

• A software application's performance like its response time,

reliability, resource usage and scalability do matter.

• The goal of Performance Testing is not to find bugs but to eliminate

performance bottlenecks.

• The focus of Performance Testing is checking a software program's

Speed - Determines whether the application responds quickly

Scalability - Determines maximum user load the software

application can handle.

Stability - Determines if the application is stable under varying loads

TRACE KTU

Performance Testing Process

TRACE KTU

1) Identify your testing environment –

Do proper requirement study & analyzing test goals and its objectives. Also

determine the testing scope along with test Initiation Checklist. Identify the

logical and physical production architecture for performance testing, identify

the software, hardware and networks configurations required for kick off the

performance testing. Compare the both test and production environments

while identifying the testing environment. Get resolve the environment-

related concerns if any, analyze that whether additional tools are required

for performance testing. This step also helps to identify the probable

challenges tester may face while performance testing.

2) Identify the performance acceptance criteria –

Identify the desired performance characteristics of the application like

Response time, Throughput and Resource utilization.

TRACE KTU

3) Plan & design performance tests –

Planning and designing performance tests involves identifying key usage

scenarios, determining appropriate variability across users, identifying and

generating test data, and specifying the metrics to be collected. Ultimately,

these items will provide the foundation for workloads and workload profiles.

The output of this stage is prerequisites for Test execution are ready, all

required resources, tools & test data are ready.

4) Configuring the test environment –

Prepare with conceptual strategy, available tools, designed tests along with

testing environment before execution. The output of this stage is configured

load-generation environment and resource-monitoring tools.

5) Implement test design –

According to test planning and design create your performance tests.

TRACE KTU

6) Execute the tests –

Collect and analyze the data.

Problem Investigation like bottlenecks (memory, disk, processor, process, cache,

network, etc.) resource usage like (memory, CPU, network, etc.,)

Generate the Performance analysis reports containing all performance attributes

of the application.

Based on the analysis prepare recommendation report.

Repeat the above test for the new build received from client after fixing the bugs

and implementing the recommendations

7) Analyze Results, Report, and Retest

Consolidate, analyze and share test results.

Based on the test report re-prioritize the test & re-execute the same. If any

specific test result within the specified metric limit & all results are between the

thresholds limits then testing of same scenario on particular configuration is

completed.

TRACE KTU

Test objectives frequently include the

following:

• Response time. For example, the product catalog must be

displayed in less than 3 seconds.

• Throughput. For example, the system must support 100

transactions per second.

• Resource utilization. A frequently overlooked aspect is the

amount of resources

your application is consuming, in terms of processor, memory,

disk input output

(I/O), and network I/O.

TRACE KTU

Types of Performance Testing

•Load test

•Stress test

•Data Volume Testing

•Storage Testing

TRACE KTU

Stress Testing

• Stress Testing is performance testing type to check the stability of software

when hardware resources are not sufficient like CPU, memory, disk space

etc.

• It is performed to find the upper limit capacity of the system and also to

determine how the system performs if the current load goes well above the

expected maximum.

• Main parameters to focus during Stress testing are “Response Time” and

“Throughput”.

• Stress testing is Negative testing where we load the software with large

number of concurrent users/processes which cannot be handled by the

systems hardware resources. This testing is also known as Fatigue testing

TRACE KTU

Usability Testing

• In usability testing basically the testers tests the ease with which the user

interfaces can be used.

• It tests that whether the application or the product built is user-friendly or not.

• Usability Testing is a black box testing technique.

• Usability testing also reveals whether users feel comfortable with your

application or Web site according to different parameters – the flow, navigation

and layout, speed and content – especially in comparison to prior or similar

applications.

• Usability Testing tests the following features of the software.

• — How easy it is to use the software.

— How easy it is to learn the software.

— How convenient is the software to end user.

TRACE KTU

Usability testing includes the following five

components:

• Learnability: How easy is it for users to accomplish basic tasks the first time

they encounter the design?

• Efficiency: How fast can experienced users accomplish tasks?

• Memorability: When users return to the design after a period of not using it,

does the user remember enough to use it effectively the next time, or does the

user have to start over again learning everything?

• Errors: How many errors do users make, how severe are these errors and how

easily can they recover from the errors?

• Satisfaction: How much does the user like using the system?

TRACE KTU

Benefits of usability testing to the end user or

the customer:

• Better quality software

• Software is easier to use

• Software is more readily accepted by users

• Shortens the learning curve for new users

TRACE KTU

Acceptance Testing

• Acceptance Testing is a level of the software testing where a system is tested for

acceptability.

• The purpose of this test is to evaluate the system’s compliance with the business

requirements and assess whether it is acceptable for delivery.

• Usually, Black Box Testing method is used in Acceptance Testing.

• Acceptance Testing is performed after System Testing and before making the system

available for actual use.

• The acceptance test cases are executed against the test data or using an acceptance test

script and then the results are compared with the expected ones.

• The goal of acceptance testing is to establish confidence in the system.

• Acceptance testing is most often focused on a validation type testing.

TRACE KTU

Acceptance Criteria

Acceptance criteria are defined on the basis of the following attributes

• Functional Correctness and Completeness

• Data Integrity

• Data Conversion

• Usability

• Performance

• Timeliness

• Confidentiality and Availability

• Installability and Upgradability

• Scalability

• Documentation

TRACE KTU

Types Of Acceptance Testing

• User Acceptance test

• Operational Acceptance test

• Contract Acceptance testing

• Compliance acceptance testing

TRACE KTU

• User Acceptance test

It focuses mainly on the functionality thereby validating the fitness-for-use

of the system by the business user. The user acceptance test is performed by

the users and application managers.

• Operational Acceptance test

Also known as Production acceptance test validates whether the system

meets the requirements for operation. In most of the organization the

operational acceptance test is performed by the system administration

before the system is released. The operational acceptance test may include

testing of backup/restore, disaster recovery, maintenance tasks and periodic

check of security vulnerabilities.

TRACE KTU

• Contract Acceptance testing

It is performed against the contract’s acceptance criteria for

producing custom developed software. Acceptance should be

formally defined when the contract is agreed.

• Compliance acceptance testing

It is also known as regulation acceptance testing is performed against

the regulations which must be adhered to, such as governmental,

legal or safety regulations.

TRACE KTU

Advantages Of Acceptance Testing

• The functions and features to be tested are known.

• The details of the tests are known and can be measured.

• The tests can be automated, which permits regression testing.

• The progress of the tests can be measured and monitored.

• The acceptability criteria are known.

Disadvantages Of Acceptance Testing

• Requires significant resources and planning.

• The tests may be a re-implementation of system tests.

• It may not uncover subjective defects in the software, since you are

only looking for defects you expect to find.

TRACE KTU

Beta Testing

• Beta Testing is also known as field testing. It takes place at customer’s site. It

sends the system/software to users who install it and use it under real-world

working conditions.

• A beta test is the second phase of software testing in which a sampling of

the intended audience tries the product out

• The goal of beta testing is to place your application in the hands of real users

outside of your own engineering team to discover any flaws or issues from

the user’s perspective that you would not want to have in your final,

released version of the application.

• Beta testing can be considered “pre-release testing.

TRACE KTU

Advantages of beta testing

• You have the opportunity to get your application into the hands of users

prior to releasing it to the general public.

• Users can install, test your application, and send feedback to you during

this beta testing period.

• Your beta testers can discover issues with your application that you may

have not noticed, such as confusing application flow, and even crashes.

• Using the feedback you get from these users, you can fix problems before

it is released to the general public.

• The more issues you fix that solve real user problems, the higher the

quality of your application when you release it to the general public.

• Having a higher-quality application when you release to the general public

will increase customer satisfaction.

• These users, who are early adopters of your application, will generate

excitement about your application.

TRACE KTU

Regression Testing

• Regression Testing is defined as a type of software testing to confirm that a recent

program or code change has not adversely affected existing features.

• Regression Testing is nothing but full or partial selection of already executed test

cases which are re-executed to ensure existing functionalities work fine.

• This testing is done to make sure that new code changes should not have side

effects on the existing functionalities. It ensures that old code still works once the

new code changes are done.

• Regression Testing is required when there is a

Change in requirements and code is modified according to the requirement

New feature is added to the software

Defect fixing

Performance issue fix

TRACE KTU

Regression Testing Techniques :

Retest All

This is one of the methods for Regression Testing in which all the tests in the

existing test bucket or suite should be re-executed. This is very expensive as

it requires huge time and resources.

Regression Test Selection

Instead of re-executing the entire test suite, it is better to select part of test

suite to be run

Test cases selected can be categorized as 1) Reusable Test Cases 2) Obsolete

Test Cases.

Re-usable Test cases can be used in succeeding regression cycles.

Obsolete Test Cases can't be used in succeeding cycles.

Prioritization of Test Cases

Prioritize the test cases depending on business impact, critical & frequently

used functionalities. Selection of test cases based on priority will greatly

reduce the regression test suite.

Selecting test cases for regression testing

It was found from industry data that good number of the defects reported by customers

were due to last minute bug fixes creating side effects and hence selecting the Test

Case for regression testing is an art and not that easy.

Effective Regression Tests can be done by selecting following test cases –

Test cases which have frequent defects

Functionalities which are more visible to the users

Test cases which verify core features of the product

Test cases of Functionalities which has undergone more and recent  changes

All Integration Test Cases

All Complex Test Cases

Boundary value test cases

Sample of Successful test cases

Sample of Failure test cases

Regression Testing Tools

If your software undergoes frequent changes, regression testing costs will escalate.

In such cases, Manual execution of test cases increases test execution time as well as costs.

Following are most important tools used for both functional and regression testing:

Selenium: This is an open source tool used for automating web applications. Selenium can be

used for browser based regression testing.

Quick Test Professional (QTP): HP Quick Test Professional is automated software designed to

automate functional and regression test cases. It uses VBScript language for automation. It is a

Data driven, Keyword based tool.

Rational Functional Tester (RFT): IBM's rational functional tester is a Java tool used to automate

the test cases of software applications. This is primarily used for automating regression test

cases and it also integrates with Rational Test Manager.

•

Black box testing

• No knowledge of internal design or code

required.

• Tests are based on requirements and

functionality

•

White box testing

•

Knowledge of the internal program design and code

required.

•

Tests are based on coverage of code

statements,branches,paths,conditions.

• Incorrect or missing functions

• Interface errors

• Errors in data structures or external database access

• Performance errors

• Initialization and termination errors

BLACK BOX - TESTING TECHNIQUE

Black box / Functional testing

•

Based on requirements and functionality

•

Not based on any knowledge of internal

design or code

•

Covers all combined parts of a system

•

Tests are data driven

White box testing / Structural testing

• Based on knowledge of internal logic of an

application's code

• Based on coverage of code statements,

branches, paths, conditions

• Tests are logic driven

Difference between black box, white box, grey box testing.
