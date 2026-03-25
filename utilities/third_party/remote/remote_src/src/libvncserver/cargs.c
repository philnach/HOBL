// Portions Copyright (c) 2026 Microsoft Corporation

/*
 *  This parses the command line arguments. It was separated from main.c by
 *  Justin Dearing <jdeari01@longisland.poly.edu>.
 */

/*
 *  LibVNCServer (C) 2001 Johannes E. Schindelin <Johannes.Schindelin@gmx.de>
 *  Original OSXvnc (C) 2001 Dan McGuirk <mcguirk@incompleteness.net>.
 *  Original Xvnc (C) 1999 AT&T Laboratories Cambridge.  
 *  All Rights Reserved.
 *
 *  see GPL (latest version) for full details
 */

#include <rfb/rfb.h>

extern int rfbStringToAddr(char *str, in_addr_t *iface);

void
rfbUsage(void)
{
    fprintf(stderr, "-rfbport port          TCP port for RFB protocol\n");
    fprintf(stderr, "-logEnable             Enable logging\n");
    fprintf(stderr, "-changeWallpaper       Change the wallpaper to wallpaper.png\n");
    fprintf(stderr, "-listen ipaddr         listen for connections only on network interface with\n");
    fprintf(stderr, "                       addr ipaddr. '-listen localhost' and hostname work too.\n");
}

/* purges COUNT arguments from ARGV at POSITION and decrements ARGC.
   POSITION points to the first non purged argument afterwards. */
void rfbPurgeArguments(int* argc,int* position,int count,char *argv[])
{
  int amount=(*argc)-(*position)-count;
  if(amount)
    memmove(argv+(*position),argv+(*position)+count,sizeof(char*)*amount);
  (*argc)-=count;
}

rfbBool 
rfbProcessArguments(rfbScreenInfoPtr rfbScreen,int* argc, char *argv[])
{
    int i,i1;

    if(!argc) return TRUE;
    
    for (i = i1 = 1; i < *argc;) {
        if (strcmp(argv[i], "-help") == 0 || strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
	    rfbUsage();
	    return FALSE;
	} else if (strcmp(argv[i], "-rfbport") == 0) { /* -rfbport port */
            if (i + 1 >= *argc) {
		rfbUsage();
		return FALSE;
	    }
	    rfbScreen->port = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-logEnable") == 0) {
	        rfbLogEnable(TRUE);
        } else if (strcmp(argv[i], "-changeWallpaper") == 0) {
	        rfbScreen->changeWallpaper = TRUE;
        } else if (strcmp(argv[i], "-topmostWindow") == 0) {
	        rfbScreen->topmostWindow = TRUE;
        } else if (strcmp(argv[i], "-listen") == 0) {  /* -listen ipaddr */
            if (i + 1 >= *argc) {
		rfbUsage();
		return FALSE;
	    }
            if (! rfbStringToAddr(argv[++i], &(rfbScreen->listenInterface))) {
                return FALSE;
            }
        }
	/* we just remove the processed arguments from the list */
	rfbPurgeArguments(argc,&i1,i-i1+1,argv);
	i=i1;
    }
    return TRUE;
}

rfbBool 
rfbProcessSizeArguments(int* width,int* height,int* bpp,int* argc, char *argv[])
{
    int i,i1;

    if(!argc) return TRUE;
    for (i = i1 = 1; i < *argc-1;) {
        if (strcmp(argv[i], "-bpp") == 0) {
               *bpp = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-width") == 0) {
               *width = atoi(argv[++i]);
        } else if (strcmp(argv[i], "-height") == 0) {
               *height = atoi(argv[++i]);
        } else {
	    i++;
	    i1=i;
	    continue;
	}
	rfbPurgeArguments(argc,&i1,i-i1,argv);
	i=i1;
    }
    return TRUE;
}

