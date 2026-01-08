<Object Oriented Design and Software Development:60>

Which phase of software development involves gathering and documenting user needs and system requirements?
- Implementation phase
- Testing phase
> Requirements analysis phase
- Maintenance phase

What is the primary purpose of the design phase in software development?
- Writing the actual code
> Creating the system architecture and detailed component designs
- Testing the software for bugs
- Deploying the software to production

Which software development methodology emphasizes iterative development with frequent releases and continuous customer feedback?
- Waterfall model
- V-Model
> Agile methodology
- Spiral model

In the Waterfall methodology, what is a key characteristic?
> Each phase must be completed before the next phase begins
- Phases can overlap and iterate
- Customer feedback is gathered continuously
- Requirements can change at any time

What does MVC stand for in architectural patterns?
- Model-View-Creator
- Module-View-Controller
> Model-View-Controller
- Model-Validator-Controller

In the MVC pattern, which component is responsible for handling user input and updating the model?
- Model
- View
> Controller
- Presenter

What is the main difference between MVC and MVP (Model-View-Presenter) patterns?
- MVP doesn't have a model component
> In MVP, the Presenter handles all presentation logic, while in MVC the View can query the Model directly
- MVC is only for web applications
- MVP requires three controllers

Which architectural pattern separates the user interface from business logic by introducing an intermediate layer?
- Singleton pattern
> Model-View (MV) pattern
- Factory pattern
- Observer pattern

What is the primary benefit of using the MVVM (Model-View-ViewModel) pattern?
- It eliminates the need for a database
> It enables better separation of concerns and supports data binding
- It makes the application run faster
- It reduces the amount of code needed

In software development, what is the purpose of the maintenance phase?
- Writing initial code
- Gathering requirements
> Fixing bugs, adding features, and updating the system after deployment
- Creating the initial design

What is a design pattern in object-oriented programming?
- A specific programming language feature
> A reusable solution to a commonly occurring problem in software design
- A type of database schema
- A testing methodology

Which category of design patterns deals with object creation mechanisms?
- Structural patterns
- Behavioral patterns
> Creational patterns
- Architectural patterns

The Singleton pattern belongs to which category of design patterns?
> Creational patterns
- Structural patterns
- Behavioral patterns
- Architectural patterns

What is the main purpose of the Singleton pattern?
- Create multiple instances efficiently
> Ensure a class has only one instance and provide a global point of access to it
- Connect incompatible interfaces
- Define a family of algorithms

The Factory Method pattern is used to:
- Combine multiple objects into a tree structure
> Define an interface for creating objects, letting subclasses decide which class to instantiate
- Attach additional responsibilities to objects dynamically
- Provide a way to access elements of a collection sequentially

Which design pattern category focuses on how classes and objects are composed to form larger structures?
- Creational patterns
> Structural patterns
- Behavioral patterns
- Concurrent patterns

The Adapter pattern is an example of which category?
- Creational pattern
> Structural pattern
- Behavioral pattern
- Architectural pattern

What problem does the Adapter pattern solve?
- Creating only one instance of a class
> Making incompatible interfaces work together
- Defining a family of algorithms
- Iterating through collections

The Decorator pattern allows you to:
- Create objects without specifying their exact classes
> Add new functionality to objects dynamically without altering their structure
- Ensure only one instance exists
- Convert interfaces

Which design pattern category is concerned with algorithms and the assignment of responsibilities between objects?
- Creational patterns
- Structural patterns
> Behavioral patterns
- Structural-behavioral patterns

The Observer pattern is classified as:
- A creational pattern
- A structural pattern
> A behavioral pattern
- An architectural pattern

What is the primary purpose of the Observer pattern?
- Create a family of related objects
- Wrap an object to provide a new interface
> Define a one-to-many dependency so that when one object changes state, all dependents are notified
- Ensure a class has only one instance

The Strategy pattern is used to:
- Combine objects into tree structures
> Define a family of algorithms, encapsulate each one, and make them interchangeable
- Create objects without specifying exact classes
- Provide a simplified interface to a complex subsystem

Which of the following are examples of creational design patterns?
> Singleton
> Factory Method
- Adapter
- Observer

Which of the following are examples of structural design patterns?
- Strategy
> Adapter
> Decorator
- Singleton

Which of the following are examples of behavioral design patterns?
- Factory Method
> Observer
> Strategy
- Decorator

In the Agile methodology, what is a "sprint"?
> A fixed time period during which specific work must be completed
- The final testing phase
- A type of design pattern
- A database optimization technique

What is the main advantage of using design patterns in software development?
- They make code execute faster
> They provide tested, proven development paradigms and improve code maintainability
- They eliminate the need for testing
- They automatically generate documentation

The Builder pattern is used to:
> Construct complex objects step by step, separating construction from representation
- Define one-to-many dependencies between objects
- Provide a surrogate or placeholder for another object
- Add responsibilities to objects dynamically

Which statement best describes the relationship between architectural patterns and design patterns?
- They are the same thing with different names
> Architectural patterns operate at a higher level of abstraction than design patterns
- Design patterns are more important than architectural patterns
- Architectural patterns are only used in web development

Which creational design pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes?
- Builder
- Singleton
> Abstract Factory
- Prototype

In the context of the Factory Method design pattern, what is the role of the `Creator` class?
- It defines the actual product objects to be created.
> It declares the factory method, which returns an object of type `Product`.
- It is responsible for configuring and assembling complex objects.
- It ensures that only one instance of a class exists.

Which structural design pattern attaches additional responsibilities to an object dynamically, providing a flexible alternative to subclassing for extending functionality?
- Adapter
- Facade
> Decorator
- Proxy

When would the Adapter design pattern be most appropriately applied?
- When you want to create new instances of a class while keeping the instantiation logic hidden.
> When you want to make two incompatible interfaces work together.
- When you need to provide a unified interface to a set of interfaces in a subsystem.
- When you want to define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified.

Which behavioral design pattern specifies an algorithm's skeleton in the superclass but lets subclasses override specific steps of the algorithm without changing its structure?
> Template Method
- Strategy
- Observer
- Iterator

A system needs to allow clients to define a family of algorithms, encapsulate each one, and make them interchangeable. Which design pattern best fits this requirement?
- Command
- State
> Strategy
- Mediator

What is the primary purpose of a UML Class Diagram in object-oriented design?
- To show the sequence of messages between objects during a specific use case.
- To model the dynamic behavior of an object as it transitions through different states.
> To represent the static structure of a system, showing classes, their attributes, operations, and relationships.
- To illustrate the deployment of software artifacts to physical nodes.

In a UML Sequence Diagram, what does a vertical dashed line below an object lifeline typically represent?
- An object's creation point
- An object's destruction point
> The period during which an object is active and performing an operation
- A message being sent from one object to another

Which of the following best describes Test-Driven Development (TDD)?
- Writing all tests after the code has been fully implemented.
- A methodology focused on manual testing and defect reporting.
> A development practice where tests are written *before* the code, driving the design and implementation.
- A process of continuously integrating code changes into a central repository.

What is the main goal of unit testing in object-oriented software development?
- To verify the functionality of the entire system from an end-user perspective.
- To ensure that all integrated modules work together correctly.
> To test individual components or methods in isolation to ensure they work as expected.
- To assess the performance and scalability of the application under load.

A "code smell" often indicates a deeper problem in the design of software. Which of the following is an example of a code smell related to class structure?
- Frequent use of comments
> Large Class (God Object)
- Short method names
- Consistent indentation

What is the primary benefit of applying refactoring techniques to existing code?
- To add new features more quickly without changing existing functionality.
- To fix bugs that appear during the testing phase.
> To improve the internal structure of software without changing its external behavior.
- To optimize code for faster execution speed on specific hardware.

Which of the following is a common challenge when designing concurrent object-oriented systems?
- Ensuring that objects are properly serialized for storage.
> Managing shared mutable state to prevent race conditions and deadlocks.
- Deciding on the appropriate inheritance hierarchy for objects.
- Optimizing the performance of single-threaded operations.

In a distributed object system, what mechanism allows an object in one process to invoke methods on an object located in another process or on a different machine?
- Polymorphism
- Encapsulation
> Remote Method Invocation (RMI) or Remote Procedure Call (RPC)
- Inheritance

Which design pattern addresses the challenge of providing a unified interface to a set of interfaces in a subsystem, making the subsystem easier to use?
- Bridge
- Decorator
> Facade
- Composite

</Object Oriented Design and Software Development>