$(document).ready(function(){
	$(".showlink").each(function(){
		$(this).click(function(){
			window.prompt("You can copy the link to that post below", document.location.protocol + "//" + document.location.hostname + $(this).attr("forumroot") + "post/" + $(this).attr("postid"));
		});
	});
	var wysisettings = {
		buttons: "bold,italic,underline,strike,|,centertext,|,img,mrcomputer1bblink,|,mrcomputer1bbquote",
		allButtons: {
			centertext: {
				title: "Center text",
				buttonText: "CENTER",
				hotkey: "ctrl+shift+c",
				transform: {
					"<center>{SELTEXT}</center>": "[center]{SELTEXT}[/center]"
				}
			},
			bigsize: {
				title: "Make text big",
				buttonText: "BIG",
				hotkey: "ctrl+shift+b",
				transform: {
					"<big>{SELTEXT}</big>": "[big]{SELTEXT}[/big]"
				}
			},
			smlsize: {
				title: "Make text small",
				buttonText: "SMALL",
				hotkey: "ctrl+shift+s",
				transform: {
					"<small>{SELTEXT}</small>": "[small]{SELTEXT}[/small]"
				}
			},
			mrcomputer1bblink: {
				title: "Insert Link",
				buttonText: "LINK",
				hotket: "ctrl+l",
				transform: {
					"<div style='color:blue' title='{URL}'>{SELTEXT}</a>": "[url](link){URL}(/link){SELTEXT}[/url]"
				},
				modal: {
					title: "Insert Link",
					width: "600px",
					tabs: [
					{
						input: [
						{param: "SELTEXT", title: "Enter link text"},
						{param: "URL", title: "Enter link URL"}
						]
					}
					]
				}
			},
			mrcomputer1bbquote: {
				title: "Quote",
				buttonText: "QUOTE",
				hotkey: "ctrl+q",
				transform: {
					"<div class='post-quote'>{SELTEXT}</div>": "[quote]{SELTEXT}[/quote]"
				}
			}
		}
	}
	$("#editornoclick").wysibb(wysisettings);
	$("#editor").click(function(){
		$(this).attr("placeholder", "");
		$(this).wysibb(wysisettings);
	});
	$(".quotebtn").each(function(){
		$(this).click(function(){
			$("#editor").attr("placeholder", "");
			$.get("../../post/" + $(this).attr("postid") + "/json/", {}, function(data){
				$("#editor").val("[quote][b]" + data.poster + " wrote:[/b]" + "\n" + data.content + "[/quote]\n\n");
				$("#editor").wysibb(wysisettings);
			}, "json");
		});
	});
});

/*
title: 'Insert Link',
					buttonText: 'Link',
					hotkey: "ctrl+shift+2",
					transform: {
						"<a href='{LINK}' target='_blank'>{SELTEXT}</a>":'[url][link]{LINK}[/link]{SELTEXT}[/url]'
					},
					modal: {
						title: "Insert Link",
						width: "600px",
						tabs: [
						{
							input: [
							{param: "LINK",title:"Enter URL"}
							]
						}
						]
					}
					*/