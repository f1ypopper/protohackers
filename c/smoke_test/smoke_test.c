#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include "thpool.h"

const char* host = "0.0.0.0";
const char* port = "5000";

void handle_connection(int conn){
    char* buffer = malloc(1024);
    int recv_bytes = 0;
    while(1){
	recv_bytes = read(conn, buffer, 1024);
        if(recv_bytes == 0){
            close(conn);
            printf("connection closed\n");
            return;
        }
        write(conn, buffer, recv_bytes);
    }
    free(buffer);
}

int main(){
    struct addrinfo hints;
    struct addrinfo *servinfo;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC; //ipv4
    hints.ai_socktype = SOCK_STREAM;//tcp
    hints.ai_flags = AI_PASSIVE;//fill my ip for me pls

    if(getaddrinfo(NULL, port, &hints, &servinfo) != 0){
        printf("getaddrinfo error\n");
        exit(1);
    }

    int server;

    if((server = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol)) == -1){
        printf("server socket error\n");
        exit(1);
    }

    int yes = 1;

    if(setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes)){
        printf("setsockopt\n");
        exit(1);
    }

    if(bind(server, servinfo->ai_addr, servinfo->ai_addrlen) == -1){
        printf("bind error\n");
        exit(1);
    }

    if(listen(server, 10) == -1){
        printf("listen error\n");
        exit(1);
    }
    printf("server listening on %s:%s\n", host, port);
    char conn_ipstr[INET_ADDRSTRLEN];
    threadpool* pool = thpool_init(5);
    while(1){
        struct sockaddr conn_addr;
        int conn_addrlen = sizeof(conn_addr);
        int conn = accept(server, (struct sockaddr* )&conn_addr, &conn_addrlen);
        inet_ntop(conn_addr.sa_family, conn_addr.sa_data, conn_ipstr, sizeof conn_ipstr);
        printf("accepted connection from %s\n", conn_ipstr);
        handle_connection(conn);
        thpool_add_work(pool, &handle_connection, conn);
    }
    thpool_destroy(pool);
    close(server);
    freeaddrinfo(servinfo);
}