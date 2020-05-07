# Changelog
All notable changes to this project will be documented in this file.

## [1.4.0]

### Added
* Installation guide to README
* SEO terms to ORES home page
* Adds 'main_edit' and 'main_creation' events to precache config. 
* Controlled evironment for loading models using minimal memory.

### Fixed
* Cache injection issue for multiple revision IDs and models.
* Use meta.stream rather than meta.topic in precache recentchange events. 
* Swagger docs for precache endpoint have been updated. 

### Changed
* Dropped revision count-based metrics from statsd reporting
* Allow POST to all v3 endpoints
* Limit ORES requests to 50 revids. 

## [1.3.1]

### Fixed
* Injection caches can be copied between multiple revisions
* Addresses yaml security issue by bumping dependency version
* ORES client does a better job of closing its socket connections

### Added
* Adds documentation about using docker
* ORES client.
* CIDR range support for rate limiting

### Changed
* Switch dependency to Flask 1.0
* Remove references to "Objective Revision Evaluation Service" -- it's just "ORES" now. 
* Use JSON as celery serializer (increased security)

### Removed
* Removed watchdog from precache service.  No longer necessary.

## [1.3.0]

### Fixed
* Always remove poolcounter lock
* More robust timeouts using SIGNALS in unix land

### Changed
* Use JSON lines for logging to logstash
* Use redis directly to de-duplicate jobs. 

### Added
* Explicit logging config hangling

## [1.2.1]

### Added
* More flexible args to the `score revisions` utility

## [1.2.0]

### Fixed
* Metrics collectors get something even when the request fails.
* Return 504 instead of 408 when a worker times out.  
* Fixed links in readme to repositories and privacy policy
* Does not de-duplicate in case of feature injection

### Added 
* Rate limiting support
* Metrics collected about rate limiter lock timing
* Support for model aliases -- re-use of models across contexts
* Adds Dockerfile
* Fallback logging config that speaks to stderr
* test_api utility

### Changed
* ORES home page now uses common styles
* Switched to event-based precache

## [1.1.0]

...




