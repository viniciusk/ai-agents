# Performance & Scalability Review

## Executive Summary
*High-level summary of the application's performance characteristics.*

## Database Schema & Architecture
*Identify missing foreign keys, poor data types, lack of indexing strategies, or normalization issues in the schema design.*

- **[Issue]**: 
  - **Location**: `path/to/migration_or_schema`
  - **Impact**: How does this impact data integrity or read/write performance?

## Bottlenecks (Data Access & Queries)
*Identify N+1 queries or inefficient data loading patterns in the application code.*

- **[Issue]**: 
  - **Location**: `path/to/file`
  - **Impact**: How does this impact response times under load?

## Bottlenecks (Compute & I/O)
*Identify synchronous third-party API calls, heavy computations in the request lifecycle, or file I/O issues.*

- **[Issue]**: 
  - **Location**: `path/to/file`
  - **Impact**: How does this degrade the user experience?

## Frontend / Asset Delivery
*Review asset bundle sizes, rendering strategies, and caching.*

- ...
