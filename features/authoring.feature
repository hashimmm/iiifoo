Feature: Author images to Mirador
    User should be able to export images from
    IIIF compliant sources to the server
    and view them in Mirador
    and delete them again

    Scenario: Export 1 image
        Given image info for 1 image(s)
            """
            {"url_root": "my.server.topleveldomain",
             "images": [
                 {"width": 250,
                  "height": 250,
                  "path": "http://server/prefix/moar_prefix/identifier",
                  "image_id": "new1",
                  "name": "some_label"}
             ],
             "manifest_category": "test manifests",
             "manifest_identifier": "test_manifest_1",
             "manifest_label": "test_manifest_1",
             "source_type": "test",
             "source_url": "N_A",
             "user": 0}
            """
          And a new manifest is specified
         When these details are exported
         Then a valid manifest should exist with this info

    Scenario: Export multiple images
        Given image info for 3 image(s)
            """
            {"url_root": "my.server.topleveldomain",
             "images": [
                 {"width": 250,
                  "height": 250,
                  "path": "http://server/prefix/moar_prefix/id2",
                  "image_id": "multi_new1",
                  "name": "label_multi_new1"},
                 {"width": 250,
                  "height": 250,
                  "path": "http://server/prefix/moar_prefix/id3",
                  "image_id": "multi_new2",
                  "name": "label_multi_new2"},
                 {"width": 250,
                  "height": 250,
                  "path": "http://server/prefix/moar_prefix/id4",
                  "image_id": "multi_new3",
                  "name": "label_multi_new3"}
             ],
             "manifest_category": "test manifests",
             "manifest_identifier": "test_manifest_2",
             "manifest_label": "test_manifest_2",
             "source_type": "test",
             "source_url": "N_A",
             "user": 0
            }
            """
          And a new manifest is specified
         When these details are exported
         Then a valid manifest should exist with this info

    Scenario: Export multiple images to existing manifest
        Given image info for 3 image(s)
            """
            {
                "url_root": "my.server.topleveldomain",
                "images": [
                    {"width": 250,
                     "height": 250,
                     "path": "http://server/prefix/moar_prefix/id5",
                     "image_id": "multi_append1",
                     "name": "label_multi_append1"},
                    {"width": 250,
                     "height": 250,
                     "path": "http://server/prefix/moar_prefix/id6",
                     "image_id": "multi_append2",
                     "name": "label_multi_append2"},
                    {"width": 250,
                     "height": 250,
                     "path": "http://server/prefix/moar_prefix/id7",
                     "image_id": "multi_append3",
                     "name": "label_multi_append3"}
                ],
                "manifest_category": "test manifests",
                "manifest_identifier": "test_manifest_2",
                "manifest_label": "test_manifest_2",
                "source_type": "test",
                "source_url": "N_A",
                "user": 0
            }
            """
          And an existing manifest with 3 images is specified
         When these details are exported
         Then image info should be appended to existing manifest
          And a valid manifest should exist with this info

    Scenario: Re-export existing images
        Given image info for 1 image(s)
            """
            {"url_root": "my.server.topleveldomain",
             "images": [
                 {"width": 350,
                  "height": 350,
                  "path": "http://server/prefix/moar_prefix/identifier",
                  "image_id": "new1",
                  "name": "some_label2"}
             ],
             "manifest_category": "test manifests",
             "manifest_identifier": "test_manifest_1",
             "manifest_label": "test_manifest_1_newlabel",
             "source_type": "test",
             "source_url": "N_A",
             "user": 0}
            """
          And an existing manifest with 1 images is specified
         When these details are exported
         Then manifest should reflect updated details

    Scenario: Export an image with annotations
        Given image info for 1 image(s)
            """
            {"url_root": "my.server.topleveldomain",
             "images": [
                 {"width": 350,
                  "height": 350,
                  "path": "http://server/prefix/moar_prefix/id8",
                  "image_id": "annotation_img1",
                  "name": "anno_img_label_1",
                  "comments": [{"text": "random comment 1"},
                               {"text": "random comment 2"}],
                  "transcriptions": [{"text": "dat transcription",
                                      "language_code": "en"}]
                  }
             ],
             "manifest_category": "test manifests",
             "manifest_identifier": "test_manifest_2",
             "manifest_label": "test_manifest_2",
             "source_type": "test",
             "source_url": "N_A",
             "user": 0}
            """
          And an existing manifest with 6 images is specified
         When these details are exported
         Then a valid manifest should exist with this info
          And manifest should contain an annotation link for each annotated image
          And annotations must be present in respective annotation lists

    Scenario: Delete some images from manifest
        Given deletion info for some images
            """
            {
                "images": [{"image_id": "multi_append_1"}],
                "source_url": "N_A",
                "source_type": "test",
                "manifest_identifier": "test_manifest_2",
                "action": "delete",
                "user": 0
            }
            """
         When deletion is attempted
         Then only this image should be deleted from manifest

    Scenario: Delete all images from manifest
        Given deletion info for all images
            """
            {
                "images": [{"image_id": "new1"},
                           {"image_id": "new1"}],
                "source_url": "N_A",
                "source_type": "test",
                "manifest_identifier": "test_manifest_1",
                "action": "delete",
                "user": 0
            }
            """
         When deletion is attempted
         Then manifest itself should be deleted
