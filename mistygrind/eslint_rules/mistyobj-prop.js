// Compare properties of `misty` object from the list of known methods.
//
// by SCL
// Copyright (c) 2019 rerobots, Inc.

"use strict";


module.exports = {
    meta: {
        type: "problem",
        schema: []
    },

    create( context ) {
        var mistyMethods = [
            "Debug",
            "AddPropertyTest",
            "RegisterEvent",
            "ChangeLED",
            "PlayAudioClip",
            "MoveHeadPosition",
            "MoveArmPosition"
        ];

        return {
            MemberExpression( node ) {
                if (node.object.name === "misty" && node.property &&
                    mistyMethods.indexOf(node.property.name) == -1) {
                    context.report({
                        node,
                        message: "unknown misty property: " + node.property.name
                    });
                }
            }
        };
    }
};
