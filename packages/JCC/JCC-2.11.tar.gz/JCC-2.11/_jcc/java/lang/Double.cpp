/*
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

#include <jni.h>
#include "JCCEnv.h"
#include "java/lang/Object.h"
#include "java/lang/Class.h"
#include "java/lang/Double.h"

namespace java {
    namespace lang {

        enum {
            mid__init_,
            mid_doubleValue,
            max_mid
        };

        Class *Double::class$ = NULL;
        jmethodID *Double::_mids = NULL;
        
        jclass Double::initializeClass()
        {
            if (!class$)
            {
                jclass cls = env->findClass("java/lang/Double");

                _mids = new jmethodID[max_mid];
                _mids[mid__init_] = env->getMethodID(cls, "<init>", "(D)V");
                _mids[mid_doubleValue] =
                    env->getMethodID(cls, "doubleValue", "()D");

                class$ = (Class *) new JObject(cls);
            }

            return (jclass) class$->this$;
        }

        Double::Double(jdouble n) : Object(env->newObject(initializeClass, &_mids, mid__init_, n)) {
        }

        jdouble Double::doubleValue() const
        {
            return env->callDoubleMethod(this$, _mids[mid_doubleValue]);
        }
    }
}


#include "structmember.h"
#include "functions.h"
#include "macros.h"

namespace java {
    namespace lang {

        static PyMethodDef t_Double__methods_[] = {
            { NULL, NULL, 0, NULL }
        };

        DECLARE_TYPE(Double, t_Double, Object, java::lang::Double,
                     abstract_init, 0, 0, 0, 0, 0);
    }
}
