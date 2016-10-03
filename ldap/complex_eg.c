
/*****************************************************************************
**                                 
** FILENAME : askey_ldap.c                        
** DESCRIPTION : askey_ldap interface                     
** AUTHOR : Andy Yang                             
** DATE : 07/10/2009 
** URL: http://blog.chinaunix.net/u1/45185/showart_2058260.html                                       
**                             
******************************************************************************/

/*****************************************************************************
** REVISION HISTORY    :                                                         **    
**                                                                            **
******************************************************************************/

/*****************************************************************************
**                                     **
** INCLUDE FILE                                 **
**                                     **
******************************************************************************/
#define LDAP_DEPRECATED 1

#include <stdio.h> 
#include <string.h> 
#include <stdlib.h> 
#include <time.h> 
#include <taskLib.h> 
#include <sys/times.h> 
#include "ldap.h" 
 
#define BASEDN "dc=askey,dc=com" 
#define SCOPE LDAP_SCOPE_SUB 

extern int ldap_unbind( LDAP *ld );
extern char *strdup(const char *s);
extern int strcasecmp(const char *s1, const char *s2);
static void myMallocError(int line)
{
    printf("malloc error!<%d>\n",line);
}
static void myAttributeFree(char **p)
{
    char **p1;
    char **p2;
    p1 = p;
    if(p1 == NULL)
        return;
    while(*p1 != NULL)
    {
        p2 = p1;
        p1++;
        free(*p2);
    }
    free(p);
}

 /************************************************************************
 Routine to manage the LDAPMod structure array
 manage memory used by the array, by each struct, and values

************************************************************************/
static void make_a_mod(LDAPMod ***modlist,int modop, char *attribute, char *value)
{
    LDAPMod **mods;
    int i;
    int j;

    mods = *modlist;

    if (mods == NULL)
    {
        mods = (LDAPMod **)malloc( sizeof(LDAPMod *));
        if (mods == NULL)
        {
            printf("make_a_mod: out of memory!\n");
            return;
        }
        mods[0] = NULL;
    }

    for ( i = 0; mods[i] != NULL; ++i )
    {
        if ( mods[i]->mod_op == modop && !strcasecmp( mods[i]->mod_type, attribute))
        {
            break;
        }
    }

    if (mods[i] == NULL)
    {
        mods = (LDAPMod **)realloc(mods,(i+2) * sizeof( LDAPMod * ));
        if (mods == NULL)
        {
            printf("make_a_mod: out of memory!\n");
            return;
        }
        mods[i] = (LDAPMod *)malloc(sizeof( LDAPMod));
        if (mods[i] == NULL)
        {
            printf("make_a_mod: out of memory!\n");
            return;
        }
        mods[i]->mod_op = modop;
        mods[i]->mod_values = NULL;
        mods[i]->mod_type = strdup(attribute);
        mods[i+1] = NULL;
    }

    if (value != NULL )
    {
        j = 0;
        if ( mods[i]->mod_values != NULL )
        {
            for ( ; mods[i]->mod_values[j] != NULL; j++ );
        }
        mods[i]->mod_values = (char **)realloc(mods[i]->mod_values,(j+2) * sizeof( char * ));
        if ( mods[i]->mod_values == NULL)
        {
            printf("make_a_mod: Memory allocation failure!\n");
            return;
        }
        mods[i]->mod_values[j] = strdup(value);
        mods[i]->mod_values[j+1] = NULL;
    }
    *modlist = mods;
}
#if 0
static void get_single_attribute(LDAP *ldap_struct, LDAPMessage *entry, char *attribute, char *value)
{
    char **valeurs;
    if ((valeurs = ldap_get_values(ldap_struct, entry, attribute)) != NULL)
    {
        strcpy(value, valeurs[0]);
        ldap_value_free(valeurs);
        printf("get_single_attribute: [%s] = [%s]\n", attribute, value);
    }
    else
    {
        value = NULL;
    }
}
#endif

static int modadd_ldap_entry(LDAP *ldap_struct,const char *baseDn,const char *filter,int flag,char *attributeName[], char *attributeValue[])/*flag:1 means Add,2 means modify*/
{
    int scope = LDAP_SCOPE_ONELEVEL;
    int rc;
    int i;
    int ldap_state;
    LDAPMessage *result;
    LDAPMod **mods;
    
    if(flag == 1)
    {
        ldap_state = LDAP_MOD_ADD;
    }
    else if(flag == 2)
    {
        ldap_state = LDAP_MOD_REPLACE;
    }
    else 
    {
        printf("How did you come here? \n");
        return -1;
    }
    rc = ldap_search_s(ldap_struct, baseDn, scope, filter, NULL, 0, &result);
    mods = NULL;
    i = 0;
    while(attributeName[i] != NULL && i < 20 && attributeValue[i] != NULL)
    {
        printf("Attribute:<%s>=<%s>\n",attributeName[i],attributeValue[i]);
        make_a_mod(&mods, ldap_state, attributeName[i], attributeValue[i]);
        i++;
    }

    switch (flag)
    {
        case 1:/*Add*/
        {
            if (ldap_count_entries(ldap_struct, result) != 0 || ldap_add_s(ldap_struct, baseDn, mods) != LDAP_SUCCESS)
            {
                ldap_msgfree( result );
                ldap_mods_free(mods, 1);
                return -1;
            }
            break;
        }

        case 2:/*Modify*/
        {
            if (rc != LDAP_SUCCESS || ldap_modify_s(ldap_struct, baseDn, mods) != LDAP_SUCCESS)
            {
                ldap_msgfree( result );
                ldap_mods_free(mods, 1);
                return -1;
            }
            break;
        }

        default:
        {
            printf("How did you come here? \n");
            ldap_msgfree( result ); 
            ldap_mods_free(mods, 1);
            return -1;
        }
    }

    ldap_mods_free(mods, 1);
    ldap_msgfree( result ); 
    return 0;
}

 int askey_ldap_open_bind
 (
     char *HostName,
     UINT16 HostPort,
     char *password,
     char *bindDn,
     char *BaseDn,
     int dblevel,
    LDAP **p_ldap
 )
{
    LDAP *ld; 
    int version, rc; 
    struct timeval timeout;
    *p_ldap = NULL;
    /* STEP 1: Get a handle to an LDAP connection and 
    set any session preferences. */ 
    if ( (ld = ldap_init((const char *) HostName, HostPort )) == NULL ) 
    { 
        printf( "ldap_init error" ); 
        return( -1 ); 
    } 
    /* Use the LDAP_OPT_PROTOCOL_VERSION session preference to specify 
    that the client is an LDAPv3 client. */ 
    version = LDAP_VERSION3; 
    ldap_set_option( ld, LDAP_OPT_PROTOCOL_VERSION, &version ); 
    ldap_set_option( ld, LDAP_OPT_DEBUG_LEVEL, &dblevel ); 
    timeout.tv_sec = 20;
    timeout.tv_usec = 0;
    ldap_set_option( ld, LDAP_OPT_TIMEOUT, &timeout );
    ldap_set_option( ld, LDAP_OPT_NETWORK_TIMEOUT, (const void *)&timeout );
    if (ldap_set_option( ld, LDAP_OPT_TIMELIMIT, (void *) &timeout )
            != LDAP_OPT_SUCCESS )
    {
        printf("Could not set LDAP_OPT_TIMELIMIT %d\n", timeout );
        return( -1 ); 
    }
    /* STEP 2: Bind to the server. 
    In this example, the client binds anonymously to the server 
    (no DN or credentials are specified). */ 
    if (strcmp(bindDn,"NULL") == 0 && strcmp(password,"NULL") != 0)
        rc = ldap_simple_bind_s( ld, NULL, password); 
    else if (strcmp(bindDn,"NULL") != 0 && strcmp(password,"NULL") == 0)
        rc = ldap_simple_bind_s( ld, bindDn, NULL); 
    else if (strcmp(bindDn,"NULL") == 0 && strcmp(password,"NULL") == 0)
        rc = ldap_simple_bind_s( ld, NULL, NULL); 
    else
        rc = ldap_simple_bind_s( ld, bindDn, password); 
    if ( rc != LDAP_SUCCESS ) 
    { 
        printf("ldap_simple_bind_s error: %s\n", ldap_err2string(rc)); 
        ldap_unbind( ld ); 
        return( -1 );
    } 

    *p_ldap = ld;
    return 0;
}
static int modAddAttributeProcess(int argc, char*argv[],LDAP **ld,char *BaseDn, char *filter,char ***AttrName,char ***AttrValue)
{
    int i = 0;
    char bindDn[256];
    char password[256];
    int dblevel; 
    char HostName[256];
    char **AttributesName;
    char **AttributesValue;
    char **p_AttributesName;
    char **p_AttributesValue;
    int HostPort;
    if(argc < 8)
    {
        printf("%s "
            " ...\n",argv[0]);
        return -1;
    }
    while(argv[i] != NULL)
    {
        i++;
    }
    strcpy(HostName,argv[1]);
    HostPort = atoi(argv[2]);
    strcpy(bindDn,argv[3]);
    strcpy(BaseDn,argv[4]);
    strcpy(filter,argv[5]);
    strcpy(password,argv[6]);
    dblevel = atoi(argv[7]);
    if((argc - 8)%2 != 0)
    {
        printf("AttributeName and AttributeValue should pair well!\n");
        return -1;
    }
    if(strcmp(filter,"NULL") != 0)
    {
        if(filter[0] == '(' && filter[strlen(filter) - 1] == ')')
        {
            printf("Add filter error!Should been included by ()\n");
            return -1;
        }
    }
    i = 0;
    if ( argc > 8)
    {    
        if( (AttributesName = malloc(sizeof(int)*((argc - 8)/2+1))) == NULL)
        {/*+1 means store NULL point,address length should be 4 multiple*/
            myMallocError(__LINE__);
            return -1;
        }
        if( (AttributesValue = malloc(sizeof(int)*((argc - 8)/2+1))) == NULL)
        {/*+1 means store NULL point,address length should be 4 multiple*/
            myMallocError(__LINE__);
            return -1;
        }
        p_AttributesName = AttributesName;
        p_AttributesValue = AttributesValue;
    }
    while( i < argc - 8)
    {
        if((*p_AttributesName = malloc(strlen(argv[8+i]) + 1)) == NULL)
        {
            myAttributeFree(AttributesName);
            myAttributeFree(AttributesValue);
            myMallocError(__LINE__);
            return -1;
        }
        strcpy(*p_AttributesName,argv[8+i]);
        p_AttributesName ++;
        i++;
        if((*p_AttributesValue = malloc(strlen(argv[8+i]) + 1)) == NULL)
        {
            myAttributeFree(AttributesName);
            myAttributeFree(AttributesValue);
            myMallocError(__LINE__);
            return -1;
        }
        strcpy(*p_AttributesValue,argv[8+i]);
        p_AttributesValue ++;
        i++;
    }
    /* Print out an informational message. */ 
    printf( "Connecting to host %s at port %d...\n\n", HostName, HostPort ); 
    i = 0;
    if(askey_ldap_open_bind(HostName,HostPort,password, bindDn, BaseDn,dblevel, ld) < 0)
    {
        myAttributeFree(AttributesName);
        myAttributeFree(AttributesValue);
        return -1;
    }
    *AttrName = AttributesName;
    *AttrValue = AttributesValue;
    return 0;
}
int askey_ldap_search(int argc, char* argv[])
{
    int i = 0;
    LDAP *ld; 
    char *dn; 
    LDAPMessage *result, *e; 
    char bindDn[256];
    char BaseDn[256];
    char password[256];
    int rc,dblevel; 
    char HostName[256];
    char filter[256];
    char hasSearchAttri = 0;
    char **Attributes;
    char **p_Attributes;
    int HostPort;
    if(argc < 8)
    {
        printf("%s ...\n",argv[0]);
        return -1;
    }
    strcpy(HostName,argv[1]);
    HostPort = atoi(argv[2]);
    strcpy(bindDn,argv[3]);
    strcpy(BaseDn,argv[4]);
    strcpy(filter,argv[5]);
    strcpy(password,argv[6]);
    dblevel = atoi(argv[7]);
    if(strcmp(filter,"NULL") != 0)
    {
        if(filter[0] == '(' && filter[strlen(filter) - 1] == ')')
        {
            printf("Add filter error!Should been included by ()\n");
            return -1;
        }
    }
    i = 0;
    if ( argc > 8)
    {
        hasSearchAttri = 1;
        if( (Attributes = malloc(sizeof(int)*(argc - 8 + 1))) == NULL)
        {/*+1 means store NULL point,address length should be 4 multiple*/
            myMallocError(__LINE__);
            return -1;
        }
        p_Attributes = Attributes;
    }
    while( i < argc - 8)
    {
        if((*p_Attributes = malloc(strlen(argv[8+i]) + 1)) == NULL)
        {
            free(Attributes);
            myMallocError(__LINE__);
            return -1;
        }
        strcpy(*p_Attributes,argv[8+i]);
        printf("Attributes[%d]:%s\n",i,argv[8+i]);
        i++;
        p_Attributes = Attributes + i;
    }
    /* Print out an informational message. */ 
    printf( "Connecting to host %s at port %d...\n\n", HostName, HostPort ); 

    if(askey_ldap_open_bind(HostName,HostPort,password, bindDn, BaseDn,dblevel, &ld) < 0)
    {
        return -1;
    }

    /* STEP 3: Perform the LDAP operations. 
    In this example, a simple search operation is performed. 
    The client iterates through each of the entries returned and 
    prints out the DN of each entry. */
    if(strcmp(BaseDn, "NULL") == 0 && hasSearchAttri == 0 && strcmp(filter, "NULL") == 0)
    {
        rc = ldap_search_ext_s( ld, NULL, SCOPE, NULL, NULL, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    if(strcmp(BaseDn, "NULL") == 0 && hasSearchAttri == 0 && strcmp(filter, "NULL") != 0)
    {
        rc = ldap_search_ext_s( ld, NULL, SCOPE, filter, NULL, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    else if(strcmp(BaseDn, "NULL") == 0 && hasSearchAttri && strcmp(filter, "NULL") == 0)
    {
        rc = ldap_search_ext_s( ld, NULL, SCOPE, NULL, (char **)Attributes, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    else if(strcmp(BaseDn, "NULL") == 0 && hasSearchAttri && strcmp(filter, "NULL") != 0)
    {
        rc = ldap_search_ext_s( ld, NULL, SCOPE, filter, (char **)Attributes, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    else if(strcmp(BaseDn, "NULL") != 0 && hasSearchAttri == 0 && strcmp(filter, "NULL") == 0)
    {
        rc = ldap_search_ext_s( ld, BaseDn, SCOPE, NULL, NULL, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    else if(strcmp(BaseDn, "NULL") != 0 && hasSearchAttri == 0 && strcmp(filter, "NULL") != 0)
    {
        rc = ldap_search_ext_s( ld, BaseDn, SCOPE, filter, NULL, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    else if(strcmp(BaseDn, "NULL") != 0 && hasSearchAttri && strcmp(filter, "NULL") == 0)
    {
        rc = ldap_search_ext_s( ld, BaseDn, SCOPE, NULL, (char **)Attributes, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    else if(strcmp(BaseDn, "NULL") != 0 && hasSearchAttri && strcmp(filter, "NULL") != 0)
    {
        rc = ldap_search_ext_s( ld, BaseDn, SCOPE, filter, (char **)Attributes, 0, 
            NULL, NULL, NULL, 0, &result ); 
    }
    if ( rc != LDAP_SUCCESS ) 
    { 
        printf("ldap_search_ext_s: %s\n", ldap_err2string(rc)); 
        ldap_unbind( ld ); 
        return( 1 ); 
    }
    i=0;
    for ( e = ldap_first_entry( ld, result ); e != NULL && i < 50;     e = ldap_next_entry( ld, e ) ) 
    { 
        i++;
        if ( (dn = ldap_get_dn( ld, e )) != NULL ) 
        { 
            printf( "dn: %s\n", dn ); 
            ldap_memfree( dn ); 
        } 
    } 
    ldap_msgfree( result ); 
    /* STEP 4: Disconnect from the server. */ 
    ldap_unbind( ld ); 
    return( 0 ); 

} 
 
int askey_ldap_add(int argc, char* argv[])
{
    LDAP *ld = NULL; 
    char BaseDn[256];
    char filter[256];
    char **AttributesName;
    char **AttributesValue;
    char **p_AttributesName;
    char **p_AttributesValue;
    if(modAddAttributeProcess(argc, argv, &ld, BaseDn, filter, &AttributesName, &AttributesValue) < 0)
    {
        printf("Add entry error!\n");
        return -1;
    }
    p_AttributesName = AttributesName;
    p_AttributesValue = AttributesValue;
    if(p_AttributesName == NULL || p_AttributesValue == NULL)
    {
        printf("Get p_AttributesName&p_AttributesValue error!\n");
        ldap_unbind(ld);
        return -1;
    }
    printf("<%d>\n",__LINE__);
    if(modadd_ldap_entry(ld, BaseDn,NULL, 1,AttributesName, AttributesValue) < 0)
    {
        printf("Add entry error!\n");
        ldap_unbind(ld);
        return -1;
    }
    myAttributeFree(AttributesName);
    myAttributeFree(AttributesValue);
    ldap_unbind(ld);
    return 0;
}
int askey_ldap_modify(int argc, char* argv[])
{
    LDAP *ld = NULL; 
    char BaseDn[256];
    char filter[256];
    char **AttributesName;
    char **AttributesValue;
    if(modAddAttributeProcess(argc, argv, &ld, BaseDn, filter, &AttributesName, &AttributesValue) < 0)
    {
        printf("Modify entry error!\n");
        return -1;
    }
    if(modadd_ldap_entry(ld, BaseDn,NULL, 2,AttributesName, AttributesValue) < 0)
    {
        printf("Modify entry error!\n");
        ldap_unbind(ld);
        return -1;
    }
    printf("Modify entry OK!\n");
    myAttributeFree(AttributesName);
    myAttributeFree(AttributesValue);
    ldap_unbind(ld);
    return 0;
}
int askey_ldap_delete(int argc, char* argv[])
{
    LDAP *ld; 
    char bindDn[256];
    char BaseDn[256];
    char password[256];
    int dblevel; 
    char HostName[256];
    int HostPort;
    if(argc !=7)
    {
        printf("%s \n",argv[0]);
        return -1;
    }
    strcpy(HostName,argv[1]);
    HostPort = atoi(argv[2]);
    strcpy(bindDn,argv[3]);
    strcpy(BaseDn,argv[4]);
    strcpy(password,argv[5]);
    dblevel = atoi(argv[6]);
    /* Print out an informational message. */ 
    printf( "Connecting to host %s at port %d...\n\n", HostName, HostPort ); 

    if(askey_ldap_open_bind(HostName,HostPort,password, bindDn, BaseDn,dblevel, &ld) < 0)
    {
        return -1;
    }
    if(ldap_delete_s(ld, BaseDn) != LDAP_SUCCESS)
    {
        printf("Delete entry error!\n");
        ldap_unbind( ld ); 
        return -1;
    }
    ldap_unbind( ld ); 
    printf("Delete entry OK!\n");
    return 0;
}

int askey_ldap_passwd(int argc, char* argv[])
{
    return 0;
}
int askey_ldap_modrdn(int argc, char* argv[])
{
    int HostPort;
    char bindDn[256];
    char password[256];
    char OldBaseDn[256];
    char NewBaseDn[256];
    char HostName[256];
    LDAP *ld;
    if(argc !=7)
    {
        printf("%s \n",argv[0]);
        printf("OldDnName:Old Distinguish Name.\n");
        printf("NewName:New CN Name.\n");
        printf("e.g.\n ldapmodrdn 10.8.1.113 389 cn=Manager,dc=askey,dc=com secret cn=exam,ou=sip,dc=askey,dc=com cn=new_exam\n");
        return -1;
    }
    strcpy(HostName,argv[1]);
    HostPort = atoi(argv[2]);
    strcpy(bindDn,argv[3]);
    strcpy(password,argv[4]);
    strcpy(OldBaseDn,argv[5]);
    strcpy(NewBaseDn,argv[6]);
    /* Print out an informational message. */ 
    printf( "Connecting to host %s at port %d...\n\n", HostName, HostPort ); 

    if(askey_ldap_open_bind(HostName,HostPort,password, bindDn, OldBaseDn, &ld) < 0)
    {
        return -1;
    }
    if(ldap_modrdn_s(ld, OldBaseDn,NewBaseDn) != LDAP_SUCCESS)
    {
        printf("Delete entry error!\n");
        ldap_unbind( ld );
        return -1;
    }
    ldap_unbind( ld ); 
    printf("Delete entry OK!\n");
    return 0;
}

