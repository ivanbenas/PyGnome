/*
 *  CurrentMover_c.h
 *  gnome
 *
 *  Created by Generic Programmer on 11/22/11.
 *  Copyright 2011 __MyCompanyName__. All rights reserved.
 *
 */

#ifndef __CurrentMover_c__
#define __CurrentMover_c__

#include "Earl.h"
#include "TypeDefs.h"
#include "CurrentMover_b.h"
#include "Mover/Mover_c.h"
#include "GEOMETRY.H"

#ifdef pyGNOME
#define TMap Map_c
#endif

class CurrentMover_c : virtual public CurrentMover_b, virtual public Mover_c {
	
public:
	CurrentMover_c (TMap *owner, char *name);
	CurrentMover_c () {}
	virtual void 		UpdateUncertaintyValues(Seconds elapsedTime);
	virtual OSErr		UpdateUncertainty(void);
	virtual OSErr		AllocateUncertainty ();
	virtual void		DisposeUncertainty ();
	
	virtual OSErr 		PrepareForModelStep();
	
	virtual WorldRect GetGridBounds(){return theWorld;}	
	virtual float		GetArrowDepth(){return 0.;}
	virtual Boolean		IAmA3DMover(){return false;}
	virtual ClassID 	GetClassID () { return TYPE_CURRENTMOVER; }
	virtual Boolean		IAm(ClassID id) { if(id==TYPE_CURRENTMOVER) return TRUE; return Mover_c::IAm(id); }
	
};

#undef TMap
#endif
