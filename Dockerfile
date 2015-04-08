FROM mongo:3.0.1
MAINTAINER Sergei Orlov
EXPOSE 27017
CMD mongod --smallfiles
