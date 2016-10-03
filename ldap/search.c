#include <ldap.h>

int main()
{
       LDAP            *ld;
       LDAPMessage     *res, *e;
       int             i;
       char            *a, *dn;
       void            *ptr;
       char            **vals;

       /* open a connection */
       if ( (ld = ldap_open( "127.0.0.1", 38989 ))
               == NULL )
               exit( 1 );

        int version = LDAP_VERSION3; 
        ldap_set_option( ld, LDAP_OPT_PROTOCOL_VERSION, &version );
       /* authenticate as nobody */
       if ( ldap_simple_bind_s( ld, "cn=root,dc=abc,dc=com", "123456" ) != LDAP_SUCCESS ) {
               ldap_perror( ld, "ldap_simple_bind_s" );
               ldap_unbind(ld);
               exit( 1 );
       }

       /* search for entries with cn of "Babs Jensen",
               return all attrs  */
       if ( ldap_search_s( ld, "ou=dian,dc=abc,dc=com",
           LDAP_SCOPE_SUBTREE, NULL, NULL, 0, &res )
           != LDAP_SUCCESS ) {
               ldap_perror( ld, "ldap_search_s" );
               exit( 1 );
       }

       /* step through each entry returned */
       for ( e = ldap_first_entry( ld, res ); e != NULL;  e = ldap_next_entry( ld, e ) ) {
               /* print its name */
               dn = ldap_get_dn( ld, e );
               printf("-------------------------------------\r\n");
               printf( "dn: %s\r\n", dn );
               free( dn );

               /* print each attribute */
               for ( a = ldap_first_attribute( ld, e, &ptr );
                       a != NULL;
                   a = ldap_next_attribute( ld, e, ptr ) ) {
                       printf( "attribute: %s\r\n", a );

                       /* print each value */
                       vals = ldap_get_values( ld, e, a );
                       for ( i = 0; vals[i] != NULL; i++ ) {
                               printf( "value: %s\r\n", vals[i] );
                       }
                       ldap_value_free( vals );
               }
       }
       printf("\r\n");
       /* free the search results */
       ldap_msgfree( res );

       /* close and free connection resources */
       ldap_unbind( ld );
       
       return 0;
}