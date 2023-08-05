/* start module: jsonrpc_cli */
$pyjs.loaded_modules['jsonrpc_cli'] = function (__mod_name__) {
	if($pyjs.loaded_modules['jsonrpc_cli'].__was_initialized__) return $pyjs.loaded_modules['jsonrpc_cli'];
	var $m = $pyjs.loaded_modules["jsonrpc_cli"];
	$m.__repr__ = function() { return "<module: jsonrpc_cli>"; };
	$m.__was_initialized__ = true;
	if ((__mod_name__ === null) || (typeof __mod_name__ == 'undefined')) __mod_name__ = 'jsonrpc_cli';
	$m.__name__ = __mod_name__;
	var $div2,$div1;

	$m['DOM'] = $p['___import___']('pyjamas.DOM', null, null, false);
	$m['Window'] = $p['___import___']('pyjamas.Window', null, null, false);
	$m['HTML'] = $p['___import___']('pyjamas.ui.HTML.HTML', null, null, false);
	$m['RootPanel'] = $p['___import___']('pyjamas.ui.RootPanel.RootPanel', null, null, false);
	$m['AbsolutePanel'] = $p['___import___']('pyjamas.ui.AbsolutePanel.AbsolutePanel', null, null, false);
	$m['Timer'] = $p['___import___']('pyjamas.Timer.Timer', null, null, false);
	$m['JSONProxy'] = $p['___import___']('pyjamas.JSONService.JSONProxy', null, null, false);
	$m['random'] = $p['___import___']('random', null);
	$m['FADE'] = (typeof ($div1=5000.0)==typeof ($div2=256) && typeof $div1=='number' && $div2 !== 0?
		$div1/$div2:
		$p['op_div']($div1,$div2));
	$m['DIVID'] = 'quotebox';
	$m['jsonrpc_cli'] = (function(){
		var $cls_definition = new Object();
		var $method;
		$cls_definition.__module__ = 'jsonrpc_cli';
		$method = $pyjs__bind_method2('__init__', function() {
			if (this.__is_instance__ === true) {
				var self = this;
			} else {
				var self = arguments[0];
			}
			var quotebox,width,$assign1,$div3,$div4,panel;
			$p['setattr'](self, 'remote', $m['JSONProxy']('/jsonrpc_srv', $p['list'](['quote'])));
			$assign1 = $pyjs_kwargs_call(null, $m['AbsolutePanel'], null, null, [{StyleName:'quotes'}]);
			$p['setattr'](self, 'panel', $assign1);
			panel = $assign1;
			quotebox = $m['DOM']['getElementById']($m['DIVID']);
			width = $p['getattr'](quotebox, 'clientWidth');
			var $tupleassign1 = $p['tuple']([width, (typeof ($div3=width)==typeof ($div4=2) && typeof $div3=='number' && $div4 !== 0?
				$div3/$div4:
				$p['op_div']($div3,$div4))]);
			self.w = $tupleassign1.__getitem__(0);
			self.h = $tupleassign1.__getitem__(1);
			panel['setSize']($p['sprintf']('%dpx', $p['getattr'](self, 'w')), $p['sprintf']('%dpx', $p['getattr'](self, 'h')));
			$m['RootPanel']($m['DIVID'])['add'](panel);
			self['setup']();
			return null;
		}
	, 1, [null,null,['self']]);
		$cls_definition['__init__'] = $method;
		$method = $pyjs__bind_method2('setup', function() {
			if (this.__is_instance__ === true) {
				var self = this;
			} else {
				var self = arguments[0];
			}

			self['remote']['quote'](self);
			return null;
		}
	, 1, [null,null,['self']]);
		$cls_definition['setup'] = $method;
		$method = $pyjs__bind_method2('onRemoteResponse', function(response, request_info) {
			if (this.__is_instance__ === true) {
				var self = this;
			} else {
				var self = arguments[0];
				response = arguments[1];
				request_info = arguments[2];
			}
			var play,quote,top,$mul2,$mul8,$mul7,$mul6,$mul5,$mul4,$mul3,$mul1,left;
			var $tupleassign2 = response;
			quote = $tupleassign2.__getitem__(0);
			play = $tupleassign2.__getitem__(1);
			left = (typeof ($mul3=(typeof ($mul1=$m['random']['random']())==typeof ($mul2=$p['getattr'](self, 'w')) && typeof $mul1=='number'?
				$mul1*$mul2:
				$p['op_mul']($mul1,$mul2)))==typeof ($mul4=0.25) && typeof $mul3=='number'?
				$mul3*$mul4:
				$p['op_mul']($mul3,$mul4));
			top = (typeof ($mul7=(typeof ($mul5=$m['random']['random']())==typeof ($mul6=$p['getattr'](self, 'h')) && typeof $mul5=='number'?
				$mul5*$mul6:
				$p['op_mul']($mul5,$mul6)))==typeof ($mul8=0.5) && typeof $mul7=='number'?
				$mul7*$mul8:
				$p['op_mul']($mul7,$mul8));
			$p['setattr'](self, 'hw', $m['HTML']($p['sprintf']('\x3Ch3\x3E%s\x3Cbr\x3E\x3Cem\x3E%s\x3C/em\x3E\x3C/h3\x3E', $p['tuple']([quote, play]))));
			self['panel']['add']($p['getattr'](self, 'hw'), left, top);
			$p['setattr'](self, 'color', 0);
			$p['setattr'](self, 'timer', $m['Timer']($m['FADE'], self));
			return null;
		}
	, 1, [null,null,['self'],['response'],['request_info']]);
		$cls_definition['onRemoteResponse'] = $method;
		$method = $pyjs__bind_method2('onRemoteError', function(error_code, error, request_info) {
			if (this.__is_instance__ === true) {
				var self = this;
			} else {
				var self = arguments[0];
				error_code = arguments[1];
				error = arguments[2];
				request_info = arguments[3];
			}

			$m['Window']['alert']($p['sprintf']('Error code: %d\x0A\x0A\x0A%s', $p['tuple']([error_code, error.__getitem__('message')])));
			return null;
		}
	, 1, [null,null,['self'],['error_code'],['error'],['request_info']]);
		$cls_definition['onRemoteError'] = $method;
		$method = $pyjs__bind_method2('onTimer', function(tid) {
			if (this.__is_instance__ === true) {
				var self = this;
			} else {
				var self = arguments[0];
				tid = arguments[1];
			}
			var $add4,$mul10,$add2,$add3,colors,$add1,$mul9;
			$p['setattr'](self, 'color', $p['__op_add']($add1=$p['getattr'](self, 'color'),$add2=1));
			colors = $p['__op_add']($add3='#',$add4=(typeof ($mul9=$p['sprintf']('%02x', $p['getattr'](self, 'color')))==typeof ($mul10=3) && typeof $mul9=='number'?
				$mul9*$mul10:
				$p['op_mul']($mul9,$mul10)));
			$m['DOM']['setStyleAttribute'](self['hw']['getElement'](), 'color', colors);
			if ($p['bool'](($p['cmp']($p['getattr'](self, 'color'), 255) == -1))) {
				$p['setattr'](self, 'timer', $m['Timer']($m['FADE'], self));
			}
			else {
				self['panel']['remove']($p['getattr'](self, 'hw'));
				self['setup']();
			}
			return null;
		}
	, 1, [null,null,['self'],['tid']]);
		$cls_definition['onTimer'] = $method;
		var $bases = new Array(pyjslib.object);
		var $data = $p['dict']();
		for (var $item in $cls_definition) { $data.__setitem__($item, $cls_definition[$item]); }
		return $p['_create_class']('jsonrpc_cli', $p['tuple']($bases), $data);
	})();
	if ($p['bool']($p['op_eq']((typeof __name__ == "undefined"?$m.__name__:__name__), '__main__'))) {
		$m['jsonrpc_cli']();
	}
	return this;
}; /* end jsonrpc_cli */


/* end module: jsonrpc_cli */


/*
PYJS_DEPS: ['pyjamas.DOM', 'pyjamas', 'pyjamas.Window', 'pyjamas.ui.HTML.HTML', 'pyjamas.ui', 'pyjamas.ui.HTML', 'pyjamas.ui.RootPanel.RootPanel', 'pyjamas.ui.RootPanel', 'pyjamas.ui.AbsolutePanel.AbsolutePanel', 'pyjamas.ui.AbsolutePanel', 'pyjamas.Timer.Timer', 'pyjamas.Timer', 'pyjamas.JSONService.JSONProxy', 'pyjamas.JSONService', 'random']
*/
