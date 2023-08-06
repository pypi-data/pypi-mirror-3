#
# Jasy - Web Tooling Framework
# Copyright 2010-2012 Zynga Inc.
#

import os, copy, zlib

from jasy.core.Error import JasyError

import jasy.js.parse.Parser as Parser
import jasy.js.parse.ScopeScanner as ScopeScanner

import jasy.js.clean.DeadCode
import jasy.js.clean.Unused
import jasy.js.clean.Permutate

import jasy.js.output.Optimization

from jasy.core.Item import Item
from jasy.core.Permutation import getPermutation
from jasy.js.api.Data import ApiData
from jasy.js.MetaData import MetaData
from jasy.js.output.Compressor import Compressor

from jasy.js.util import *

from jasy.i18n.Translation import hasText

from jasy.core.Logging import * 

try:
    from pygments import highlight
    from pygments.lexers import JavascriptLexer
    from pygments.formatters import HtmlFormatter
except:
    highlight = None


aliases = {}

defaultOptimization = jasy.js.output.Optimization.Optimization("declarations", "blocks", "variables")
defaultPermutation = getPermutation({"debug" : False})


__all__ = ["Class", "Error"]


def collectFields(node, keys=None):
    
    if keys is None:
        keys = set()
    
    # Always the first parameter
    # Supported calls: core.Env.isSet(key, expected?), core.Env.getValue(key), core.Env.select(key, map)
    calls = ("core.Env.isSet", "core.Env.getValue", "core.Env.select")
    if node.type == "dot" and node.parent.type == "call" and assembleDot(node) in calls:
        keys.add(node.parent[1][0].value)

    # Process children
    for child in reversed(node):
        if child != None:
            collectFields(child, keys)
            
    return keys


class ClassError(Exception):
    def __init__(self, inst, msg):
        self.__msg = msg
        self.__inst = inst
        
    def __str__(self):
        return "Error processing class %s: %s" % (self.__inst, self.__msg)


class Class(Item):
    
    kind = "class"
    
    def __getTree(self, context=None):
        
        field = "tree[%s]" % self.id
        tree = self.project.getCache().read(field, self.mtime)
        if not tree:
            info("Processing class %s %s...", colorize(self.id, "bold"), colorize("[%s]" % context, "cyan"))
            
            indent()
            tree = Parser.parse(self.getText(), self.id)
            ScopeScanner.scan(tree)
            outdent()
            
            self.project.getCache().store(field, tree, self.mtime, True)
        
        return tree
    
    
    def __getOptimizedTree(self, permutation=None, context=None):
        """Returns an optimized tree with permutations applied"""

        field = "opt-tree[%s]-%s" % (self.id, permutation)
        tree = self.project.getCache().read(field, self.mtime)
        if not tree:
            tree = copy.deepcopy(self.__getTree("%s:plain" % context))

            # Logging
            msg = "Processing class %s" % colorize(self.id, "bold")
            if permutation:
                msg += colorize(" (%s)" % permutation, "grey")
            if context:
                msg += colorize(" [%s]" % context, "cyan")
                
            info("%s..." % msg)
            indent()

            # Apply permutation
            if permutation:
                jasy.js.clean.Permutate.patch(tree, permutation)

            # Cleanups
            jasy.js.clean.DeadCode.cleanup(tree)
            ScopeScanner.scan(tree)
            jasy.js.clean.Unused.cleanup(tree)
        
            self.project.getCache().store(field, tree, self.mtime, True)
            outdent()

        return tree


    def getDependencies(self, permutation=None, classes=None, warnings=True):
        """ 
        Returns a set of dependencies seen through the given list of known 
        classes (ignoring all unknown items in original set). This method
        makes use of the meta data (see core/MetaData.py) and the variable data 
        (see parse/ScopeData.py).
        """
        
        permutation = self.filterPermutation(permutation)
        
        meta = self.getMetaData(permutation)
        scope = self.getScopeData(permutation)
        
        result = set()
        
        # Manually defined names/classes
        for name in meta.requires:
            if name != self.id and name in classes and classes[name].kind == "class":
                result.add(classes[name])
            elif warnings:
                warn("- Missing class (required): %s in %s", name, self.id)

        # Globally modified names (mostly relevant when working without namespaces)
        for name in scope.shared:
            if name != self.id and name in classes and classes[name].kind == "class":
                result.add(classes[name])
        
        # Add classes from detected package access
        for package in scope.packages:
            if package in aliases:
                className = aliases[package]
                if className in classes:
                    result.add(classes[className])
                    continue
            
            orig = package
            while True:
                if package == self.id:
                    break
            
                elif package in classes and classes[package].kind == "class":
                    aliases[orig] = package
                    result.add(classes[package])
                    break
            
                else:
                    pos = package.rfind(".")
                    if pos == -1:
                        break
                    
                    package = package[0:pos]
                    
        # Manually excluded names/classes
        for name in meta.optionals:
            if name != self.id and name in classes and classes[name].kind == "class":
                result.remove(classes[name])
            elif warnings:
                warn("- Missing class (optional): %s in %s", name, self.id)
        
        return result
        
        
    def getScopeData(self, permutation=None):
        """
        Returns the top level scope object which contains information about the
        global variable and package usage/influence.
        """
        
        permutation = self.filterPermutation(permutation)
        
        field = "scope[%s]-%s" % (self.id, permutation)
        scope = self.project.getCache().read(field, self.mtime)
        if scope is None:
            scope = self.__getOptimizedTree(permutation, "scope").scope
            self.project.getCache().store(field, scope, self.mtime)
        
        return scope
        
        
    def getApi(self):
        field = "api[%s]" % self.id
        apidata = self.project.getCache().read(field, self.mtime)
        if apidata is None:
            apidata = ApiData(self.id)
            
            tree = self.__getTree(context="api")
            indent()
            apidata.scanTree(tree)
            outdent()
            
            metaData = self.getMetaData()
            apidata.addAssets(metaData.assets)
            for require in metaData.requires:
                apidata.addUses(require)
            for optional in metaData.optionals:
                apidata.removeUses(optional)
                
            apidata.addSize(self.getSize())
            apidata.addFields(self.getFields())
            
            self.project.getCache().store(field, apidata, self.mtime)

        return apidata


    def getHighlightedCode(self):
        field = "highlighted[%s]" % self.id
        source = self.project.getCache().read(field, self.mtime)
        if source is None:
            if highlight is None:
                raise JasyError("Could not highlight JavaScript code! Please install Pygments.")
            
            lexer = JavascriptLexer(tabsize=2)
            formatter = HtmlFormatter(full=True, style="autumn", linenos="table", lineanchors="line")
            source = highlight(self.getText(), lexer, formatter)
            
            self.project.getCache().store(field, source, self.mtime)

        return source


    def getMetaData(self, permutation=None):
        permutation = self.filterPermutation(permutation)
        
        field = "meta[%s]-%s" % (self.id, permutation)
        meta = self.project.getCache().read(field, self.mtime)
        if meta is None:
            meta = MetaData(self.__getOptimizedTree(permutation, "meta"))
            self.project.getCache().store(field, meta, self.mtime)
            
        return meta
        
        
    def getFields(self):
        field = "fields[%s]" % (self.id)
        fields = self.project.getCache().read(field, self.mtime)
        if fields is None:
            fields = collectFields(self.__getTree(context="fields"))
            self.project.getCache().store(field, fields, self.mtime)
        
        return fields


    def usesTranslation(self):
        field = "translation[%s]" % (self.id)
        result = self.project.getCache().read(field, self.mtime)
        if result is None:
            result = hasText(self.__getTree(context="i18n"))
            self.project.getCache().store(field, result, self.mtime)
        
        return result
        
        
    def filterPermutation(self, permutation):
        if permutation:
            fields = self.getFields()
            if fields:
                return permutation.filter(fields)

        return None
        
        
    def filterTranslation(self, translation):
        if translation and self.usesTranslation():
            return translation
            
        return None
        
        
    def getCompressed(self, permutation=None, translation=None, optimization=None, formatting=None, context="compressed"):
        permutation = self.filterPermutation(permutation)
        translation = self.filterTranslation(translation)
        
        field = "compressed[%s]-%s-%s-%s-%s" % (self.id, permutation, translation, optimization, formatting)
        compressed = self.project.getCache().read(field, self.mtime)
        if compressed == None:
            tree = self.__getOptimizedTree(permutation, context)
            
            if translation or optimization:
                tree = copy.deepcopy(tree)
            
                if translation:
                    translation.patch(tree)

                if optimization:
                    try:
                        optimization.apply(tree)
                    except jasy.js.output.Optimization.Error as error:
                        raise ClassError(self, "Could not compress class! %s" % error)
                
            compressed = Compressor(formatting).compress(tree)
            self.project.getCache().store(field, compressed, self.mtime)
            
        return compressed
            
            
    def getSize(self):
        field = "size[%s]" % self.id
        size = self.project.getCache().read(field, self.mtime)
        
        if size is None:
            compressed = self.getCompressed(context="size")
            optimized = self.getCompressed(permutation=defaultPermutation, optimization=defaultOptimization, context="size")
            zipped = zlib.compress(optimized.encode("utf-8"))
            
            size = {
                "compressed" : len(compressed),
                "optimized" : len(optimized),
                "zipped" : len(zipped)
            }
            
            self.project.getCache().store(field, size, self.mtime)
            
        return size
        
        
