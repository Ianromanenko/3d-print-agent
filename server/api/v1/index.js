import { Router } from 'express';
import { router as search }   from './search.js';
import { router as download } from './download.js';
import { router as slice }    from './slice.js';
import { router as print }    from './print.js';
import { router as status }   from './status.js';
import { router as wizard }   from './wizard.js';

export const v1 = Router();
v1.use('/search',   search);
v1.use('/download', download);
v1.use('/slice',    slice);
v1.use('/print',    print);
v1.use('/status',   status);
v1.use('/wizard',   wizard);
