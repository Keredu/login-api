sort env vars by name
```
env -0 | sort -z | tr '\0' '\n'
```


## NOTES
### DB Driver
Choosing between psycopg3 and asyncpg for your PostgreSQL database interactions in a Python application depends on several factors, including your specific use case, performance requirements, and familiarity with asynchronous programming. Both libraries are well-regarded, but they have different strengths and use cases.

Psycopg3:
Synchronous & Asynchronous: Psycopg3 supports both synchronous and asynchronous operations. This can be beneficial if you have a mix of synchronous and asynchronous code in your application.
Feature-Rich: It is a mature library with a wide range of PostgreSQL features supported.
Widely Used: Being the successor to psycopg2, it inherits a large user base and is commonly used in the Python community.
asyncpg:
Asynchronous-First: asyncpg is an asynchronous PostgreSQL client designed specifically for use with asyncio. It is highly optimized for asynchronous operations.
Performance: Known for its high performance, asyncpg is often faster than other PostgreSQL clients in Python, especially in applications with heavy I/O operations.
Less Overhead: Designed with the focus on performance and minimal overhead for database operations.
Considerations for Decision Making:
Application Architecture:

If your application is already using or planning to use asynchronous programming extensively (e.g., with FastAPI or asyncio), asyncpg might be a more natural fit.
For applications with a mix of synchronous and asynchronous code or for those gradually transitioning to async, psycopg3 could be more flexible.
Performance Requirements:

If your application demands maximum performance and is I/O bound, especially with high database transaction rates, asyncpg is often recommended for its superior performance.
Feature Requirements:

Consider the specific features of PostgreSQL that you need. While both libraries support a wide range of features, there might be differences in advanced feature support.
Learning Curve and Complexity:

If your team is more comfortable with synchronous programming or if you want to avoid the additional complexity of asynchronous code, psycopg3 might be preferable.
Community and Support:

Both libraries are well-supported, but psycopg3, being a successor to the very popular psycopg2, might have a larger community for support.
Recommendation:
If your application heavily relies on asyncio or if you require maximum performance for high-load asynchronous operations, go with asyncpg.
If you prefer a more traditional approach, require a mix of synchronous and asynchronous operations, or if you are upgrading from psycopg2, then psycopg3 would be a suitable choice.
In the end, the best choice depends on your specific application's needs, your team's expertise, and your future development plans. It's also worth noting that you can switch between these libraries later if your requirements change, although it would require some refactoring.